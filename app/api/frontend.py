"""前端页面 — 直接用 jinja2 渲染"""

from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))

router = APIRouter(tags=["前端页面"])


@router.get("/login", response_class=HTMLResponse)
async def login_page():
    template = env.get_template("login.html")
    return HTMLResponse(template.render())


@router.get("/", response_class=HTMLResponse)
async def tasks_page():
    template = env.get_template("tasks.html")
    return HTMLResponse(template.render())
