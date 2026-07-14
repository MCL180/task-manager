"""FastAPI 应用入口"""

from fastapi import FastAPI

from app.api import auth, tasks, tags
from app.database import engine, Base

# 建表（生产环境用 Alembic，开发阶段直接 create_all）
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Task Manager API",
    description="个人任务管理系统后端 —— 支持多用户、任务 CRUD、标签分类、天气 API 集成",
    version="1.0.0",
)

app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(tags.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
