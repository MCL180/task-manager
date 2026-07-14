"""标签路由"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.tag import Tag
from app.schemas.tag import TagCreate, TagOut

router = APIRouter(prefix="/api/v1/tags", tags=["标签"])


@router.get("", response_model=list[TagOut])
def list_tags(db: Session = Depends(get_db), user_id: int = Depends(get_current_user)):
    """获取所有标签"""
    return db.query(Tag).all()


@router.post("", response_model=TagOut, status_code=status.HTTP_201_CREATED)
def create_tag(body: TagCreate, db: Session = Depends(get_db), user_id: int = Depends(get_current_user)):
    """创建标签"""
    existing = db.query(Tag).filter(Tag.name == body.name).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="标签已存在")
    tag = Tag(name=body.name)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(tag_id: int, db: Session = Depends(get_db), user_id: int = Depends(get_current_user)):
    """删除标签"""
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")
    db.delete(tag)
    db.commit()
