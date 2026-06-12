"""Подключение к БД и создание таблиц."""
from __future__ import annotations

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from backend.config import ADMIN_PASSWORD, ADMIN_USERNAME, DATABASE_URL
from backend.passwords import hash_password

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def _migrate_schema() -> None:
    with engine.begin() as conn:
        conn.execute(
            text("ALTER TABLE attempts ADD COLUMN IF NOT EXISTS last_archive_key VARCHAR(1000)")
        )
        conn.execute(
            text(
                "ALTER TABLE attempts ADD COLUMN IF NOT EXISTS "
                "last_generated_at TIMESTAMPTZ"
            )
        )
        conn.execute(
            text("ALTER TABLE attempts ADD COLUMN IF NOT EXISTS user_id VARCHAR(36)")
        )


def _ensure_admin_user() -> None:
    from backend.models import User

    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.username == ADMIN_USERNAME).first()
        if admin is None:
            admin = User(
                username=ADMIN_USERNAME,
                password_hash=hash_password(ADMIN_PASSWORD),
                is_active=True,
            )
            db.add(admin)
        else:
            admin.password_hash = hash_password(ADMIN_PASSWORD)
            admin.is_active = True
        db.commit()
    finally:
        db.close()


def init_db() -> None:
    from backend import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    _migrate_schema()
    _ensure_admin_user()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
