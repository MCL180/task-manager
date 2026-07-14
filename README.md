# Task Manager

个人任务管理系统后端 —— Python + FastAPI + SQLAlchemy + 天气 API 集成

## 技术栈

| 分类 | 技术 |
|------|------|
| Web 框架 | FastAPI |
| ORM | SQLAlchemy |
| 数据库 | SQLite（可切换 MySQL/PostgreSQL） |
| 认证 | JWT（python-jose + bcrypt） |
| API 调用 | httpx + Open-Meteo 免费天气 API |
| 部署 | Docker + docker-compose + Nginx |

## 快速启动

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 启动服务
uvicorn app.main:app --host 0.0.0.0 --port 8000

# 3. 打开 Swagger 文档
# 浏览器访问 http://localhost:8000/docs
```

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/auth/register` | 用户注册 |
| POST | `/api/v1/auth/login` | 用户登录 |
| GET | `/api/v1/tasks` | 任务列表（支持按状态/优先级/标签筛选） |
| POST | `/api/v1/tasks` | 创建任务（自动获取城市天气） |
| GET | `/api/v1/tasks/{id}` | 任务详情 |
| PUT | `/api/v1/tasks/{id}` | 编辑任务 |
| DELETE | `/api/v1/tasks/{id}` | 删除任务 |
| GET | `/api/v1/tags` | 标签列表 |
| POST | `/api/v1/tags` | 创建标签 |
| DELETE | `/api/v1/tags/{id}` | 删除标签 |

## Docker 部署

```bash
docker compose up -d
```

## 项目结构

```
├── app/
│   ├── main.py              # FastAPI 入口
│   ├── config.py            # 配置（环境变量）
│   ├── database.py          # 数据库引擎
│   ├── models/              # SQLAlchemy 模型
│   │   ├── user.py          # 用户表
│   │   ├── task.py          # 任务表 + 天气快照
│   │   └── tag.py           # 标签表 + 多对多中间表
│   ├── schemas/             # Pydantic 请求/响应模型
│   ├── api/                 # 路由接口
│   │   ├── auth.py          # 注册/登录
│   │   ├── tasks.py         # 任务 CRUD
│   │   └── tags.py          # 标签管理
│   ├── services/            # 业务逻辑
│   │   ├── auth_service.py  # 密码哈希 + JWT 签发
│   │   └── weather_service.py  # 第三方 API 调用
│   └── middleware/
│       └── auth.py          # JWT 鉴权中间件
├── Dockerfile
├── docker-compose.yml
├── nginx.conf
└── requirements.txt
```
