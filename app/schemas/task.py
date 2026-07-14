from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    priority: str = "medium"          # low / medium / high
    status: str = "todo"              # todo / in_progress / done
    city: str | None = None           # 城市名，用于获取天气
    tag_ids: list[int] = []           # 关联的标签 ID


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    priority: str | None = None
    status: str | None = None
    city: str | None = None
    tag_ids: list[int] | None = None


class TaskWeatherOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    city: str
    weather_json: str | None


class TaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    status: str
    priority: str
    city: str | None
    created_at: datetime
    updated_at: datetime
    user_id: int
    tags: list["TagOut"] = []
    weather: TaskWeatherOut | None = None


class TaskListOut(BaseModel):
    total: int
    items: list[TaskOut]


from app.schemas.tag import TagOut
