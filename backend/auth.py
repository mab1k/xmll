"""Аутентификация: пароли и JWT."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from backend.config import ADMIN_USERNAME, JWT_EXPIRE_HOURS, JWT_SECRET
from backend.db import get_db
from backend.models import User

security = HTTPBearer(auto_error=False)


def create_access_token(user: User) -> str:
    payload = {
        "sub": user.id,
        "username": user.username,
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRE_HOURS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=401, detail="Недействительный токен") from exc


def is_env_admin(user: User) -> bool:
    return user.username == ADMIN_USERNAME


def user_to_dict(user: User) -> dict:
    return {
        "id": user.id,
        "username": user.username,
        "isAdmin": is_env_admin(user),
        "isActive": user.is_active,
        "createdAt": user.created_at.isoformat(),
    }


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Требуется авторизация")
    payload = decode_token(credentials.credentials)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Недействительный токен")
    user = db.get(User, user_id)
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="Пользователь не найден")
    return user


def require_env_admin(user: User = Depends(get_current_user)) -> User:
    if not is_env_admin(user):
        raise HTTPException(status_code=403, detail="Доступ только для администратора")
    return user
