"""Управление пользователями (админка)."""
from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.auth import is_env_admin, user_to_dict
from backend.passwords import hash_password, verify_password
from backend.models import User


def list_users(db: Session) -> list[dict]:
    rows = db.query(User).order_by(User.created_at.asc()).all()
    return [user_to_dict(row) for row in rows]


def create_user(db: Session, *, username: str, password: str) -> dict:
    username = username.strip()
    if not username:
        raise HTTPException(status_code=400, detail="Укажите логин")
    if len(password) < 4:
        raise HTTPException(status_code=400, detail="Пароль должен быть не короче 4 символов")
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=400, detail="Пользователь с таким логином уже существует")
    user = User(username=username, password_hash=hash_password(password), is_active=True)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user_to_dict(user)


def update_user(
    db: Session,
    user_id: str,
    *,
    username: str | None = None,
    password: str | None = None,
    is_active: bool | None = None,
    current_admin: User,
) -> dict:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    if is_env_admin(user) and user.id != current_admin.id:
        if username and username != user.username:
            raise HTTPException(status_code=400, detail="Нельзя переименовать главного администратора")
        if is_active is False:
            raise HTTPException(status_code=400, detail="Нельзя деактивировать главного администратора")

    if username is not None:
        username = username.strip()
        if not username:
            raise HTTPException(status_code=400, detail="Укажите логин")
        exists = db.query(User).filter(User.username == username, User.id != user_id).first()
        if exists:
            raise HTTPException(status_code=400, detail="Пользователь с таким логином уже существует")
        user.username = username

    if password:
        if len(password) < 4:
            raise HTTPException(status_code=400, detail="Пароль должен быть не короче 4 символов")
        user.password_hash = hash_password(password)

    if is_active is not None:
        if user.id == current_admin.id and not is_active:
            raise HTTPException(status_code=400, detail="Нельзя деактивировать себя")
        user.is_active = is_active

    db.commit()
    db.refresh(user)
    return user_to_dict(user)


def delete_user(db: Session, user_id: str, *, current_admin: User) -> None:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    if user.id == current_admin.id:
        raise HTTPException(status_code=400, detail="Нельзя удалить себя")
    if is_env_admin(user):
        raise HTTPException(status_code=400, detail="Нельзя удалить главного администратора")
    db.delete(user)
    db.commit()


def authenticate(db: Session, username: str, password: str) -> User:
    user = db.query(User).filter(User.username == username.strip()).first()
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")
    if not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")
    return user
