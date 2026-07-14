"""任务相关路由：CRUD + 天气"""

import json

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.task import Task, TaskWeather, TaskStatus, TaskPriority
from app.models.tag import Tag
from app.schemas.task import TaskCreate, TaskUpdate, TaskOut, TaskListOut, TaskWeatherOut
from app.services import weather_service

router = APIRouter(prefix="/api/v1/tasks", tags=["任务"])


def _task_to_out(task: Task) -> dict:
    """把 ORM 对象转成字典，包含标签和天气"""
    weather_out = None
    if task.weather:
        weather_out = TaskWeatherOut.model_validate(task.weather)

    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "status": task.status.value,
        "priority": task.priority.value,
        "city": task.city,
        "created_at": task.created_at,
        "updated_at": task.updated_at,
        "user_id": task.user_id,
        "tags": [{"id": t.id, "name": t.name} for t in task.tags],
        "weather": weather_out,
    }


@router.get("", response_model=TaskListOut)
def list_tasks(
    status_filter: str | None = Query(None, alias="status"),
    priority_filter: str | None = Query(None, alias="priority"),
    tag_id: int | None = Query(None),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user),
):
    """获取当前用户的任务列表，支持按状态/优先级/标签筛选"""
    query = db.query(Task).filter(Task.user_id == user_id)

    if status_filter:
        query = query.filter(Task.status == TaskStatus(status_filter))
    if priority_filter:
        query = query.filter(Task.priority == TaskPriority(priority_filter))
    if tag_id is not None:
        query = query.filter(Task.tags.any(Tag.id == tag_id))

    tasks = query.order_by(Task.created_at.desc()).all()
    return TaskListOut(total=len(tasks), items=[_task_to_out(t) for t in tasks])


@router.get("/{task_id}", response_model=TaskOut)
def get_task(task_id: int, db: Session = Depends(get_db), user_id: int = Depends(get_current_user)):
    """获取单个任务详情（含天气快照）"""
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == user_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return _task_to_out(task)


@router.post("", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
async def create_task(body: TaskCreate, db: Session = Depends(get_db), user_id: int = Depends(get_current_user)):
    """创建任务。如果传了 city，自动调用和风天气 API 并保存快照"""
    task = Task(
        title=body.title,
        description=body.description,
        status=TaskStatus(body.status),
        priority=TaskPriority(body.priority),
        city=body.city,
        user_id=user_id,
    )

    # 关联标签
    if body.tag_ids:
        tags = db.query(Tag).filter(Tag.id.in_(body.tag_ids)).all()
        task.tags = tags

    db.add(task)
    db.flush()  # 先 flush 拿 task.id

    # 调用第三方天气 API
    if body.city:
        weather_data = await weather_service.get_weather(body.city)
        weather_record = TaskWeather(
            task_id=task.id,
            city=body.city,
            weather_json=json.dumps(weather_data, ensure_ascii=False),
        )
        db.add(weather_record)

    db.commit()
    db.refresh(task)
    return _task_to_out(task)


@router.put("/{task_id}", response_model=TaskOut)
async def update_task(
    task_id: int,
    body: TaskUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user),
):
    """编辑任务。如果城市变了，重新获取天气"""
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == user_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    # 更新简单字段
    for field in ("title", "description", "city"):
        val = getattr(body, field)
        if val is not None:
            setattr(task, field, val)
    if body.status is not None:
        task.status = TaskStatus(body.status)
    if body.priority is not None:
        task.priority = TaskPriority(body.priority)

    # 更新标签
    if body.tag_ids is not None:
        tags = db.query(Tag).filter(Tag.id.in_(body.tag_ids)).all()
        task.tags = tags

    # 城市变了 → 重新获取天气
    if body.city is not None:
        weather_data = await weather_service.get_weather(body.city)
        if task.weather:
            task.weather.city = body.city
            task.weather.weather_json = json.dumps(weather_data, ensure_ascii=False)
        else:
            db.add(TaskWeather(
                task_id=task.id,
                city=body.city,
                weather_json=json.dumps(weather_data, ensure_ascii=False),
            ))

    db.commit()
    db.refresh(task)
    return _task_to_out(task)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db), user_id: int = Depends(get_current_user)):
    """删除任务"""
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == user_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    db.delete(task)
    db.commit()
