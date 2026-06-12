"""Настройки приложения из переменных окружения."""
from __future__ import annotations

import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://xmll:xmll@localhost:5432/xmll",
)

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "conclusion-files")
MINIO_SECURE = os.getenv("MINIO_SECURE", "false").lower() in {"1", "true", "yes"}

JWT_SECRET = os.getenv("JWT_SECRET", "change-me-in-production")
JWT_EXPIRE_HOURS = int(os.getenv("JWT_EXPIRE_HOURS", "72"))

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin")
