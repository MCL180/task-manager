"""FastAPI 应用入口"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api import auth, tasks, tags, frontend
from app.database import engine, Base

# 建表
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Task Manager API",
    description="个人任务管理系统 —— 支持多用户、任务 CRUD、标签分类、天气 API 集成",
    version="1.0.0",
)

# 静态文件（CSS）
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# API 路由
app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(tags.router)

# 前端页面路由（放在最后，避免覆盖 API 路由）
app.include_router(frontend.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
