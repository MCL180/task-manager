"""用户认证服务：注册、登录、JWT 签发"""

from datetime import datetime, timedelta

import bcrypt
from sqlalchemy.orm import Session
from jose import jwt

from app.config import settings
from app.models.user import User


def hash_password(password: str) -> str:
    """明文密码 → bcrypt 哈希"""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证明文与哈希是否匹配"""
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def create_access_token(user_id: int) -> str:
    """签发 JWT，payload 包含 user_id 和过期时间"""
    expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {"user_id": user_id, "exp": expire}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def register_user(db: Session, username: str, password: str) -> User | None:
    """注册。成功返回 User，用户名已存在返回 None"""
    existing = db.query(User).filter(User.username == username).first()
    if existing:
        return None
    user = User(username=username, password_hash=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def login_user(db: Session, username: str, password: str) -> str | None:
    """登录。成功返回 JWT Token，失败返回 None"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return create_access_token(user.id)
