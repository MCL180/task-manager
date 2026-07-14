from sqlalchemy import Table, Column, Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

# 多对多中间表
task_tag_table = Table(
    "task_tags",
    Base.metadata,
    Column("task_id", ForeignKey("tasks.id"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id"), primary_key=True),
)


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    tasks: Mapped[list["Task"]] = relationship(
        "Task",
        secondary=task_tag_table,
        back_populates="tags",
    )

    def __repr__(self) -> str:
        return f"<Tag(id={self.id}, name={self.name})>"
