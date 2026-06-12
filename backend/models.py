"""Модели БД для сохранённых попыток генерации."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    attempts: Mapped[list["Attempt"]] = relationship("Attempt", back_populates="owner")


class Attempt(Base):
    __tablename__ = "attempts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(500), nullable=False, default="Без названия")
    form_data: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=_utcnow,
        onupdate=_utcnow,
    )
    last_archive_key: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    last_generated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    owner: Mapped[User | None] = relationship("User", back_populates="attempts")
    files: Mapped[list[StoredFile]] = relationship(
        "StoredFile",
        back_populates="attempt",
        cascade="all, delete-orphan",
    )


class StoredFile(Base):
    __tablename__ = "stored_files"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    attempt_id: Mapped[str] = mapped_column(String(36), ForeignKey("attempts.id", ondelete="CASCADE"))
    original_name: Mapped[str] = mapped_column(String(500), nullable=False)
    content_type: Mapped[str] = mapped_column(String(120), nullable=False, default="application/octet-stream")
    object_key: Mapped[str] = mapped_column(String(1000), nullable=False)

    attempt: Mapped[Attempt] = relationship("Attempt", back_populates="files")
