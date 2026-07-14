from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import String, Text, Integer, DateTime, Enum, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.tag import task_tag_table


class TaskStatus(str, PyEnum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class TaskPriority(str, PyEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus), default=TaskStatus.TODO, nullable=False
    )
    priority: Mapped[TaskPriority] = mapped_column(
        Enum(TaskPriority), default=TaskPriority.MEDIUM, nullable=False
    )
    city: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)

    owner: Mapped["User"] = relationship("User", back_populates="tasks")
    tags: Mapped[list["Tag"]] = relationship("Tag", secondary=task_tag_table, back_populates="tasks")
    weather: Mapped["TaskWeather | None"] = relationship(
        "TaskWeather", back_populates="task", uselist=False, cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Task(id={self.id}, title={self.title}, status={self.status})>"


class TaskWeather(Base):
    __tablename__ = "task_weather"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    task_id: Mapped[int] = mapped_column(Integer, ForeignKey("tasks.id"), unique=True, nullable=False)
    city: Mapped[str] = mapped_column(String(50), nullable=False)
    weather_json: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    task: Mapped["Task"] = relationship("Task", back_populates="weather")

    def __repr__(self) -> str:
        return f"<TaskWeather(task_id={self.task_id}, city={self.city})>"
