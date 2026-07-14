"""认证相关路由：注册 / 登录"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.auth import UserRegister, UserLogin, TokenResponse, UserOut
from app.services import auth_service

router = APIRouter(prefix="/api/v1/auth", tags=["认证"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(body: UserRegister, db: Session = Depends(get_db)):
    """用户注册"""
    user = auth_service.register_user(db, body.username, body.password)
    if user is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="用户名已存在")
    return user


@router.post("/login", response_model=TokenResponse)
def login(body: UserLogin, db: Session = Depends(get_db)):
    """用户登录，返回 JWT Token"""
    token = auth_service.login_user(db, body.username, body.password)
    if token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")
    return TokenResponse(access_token=token)
