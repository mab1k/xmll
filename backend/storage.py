"""Хранение файлов в MinIO."""
from __future__ import annotations

import io
import time
from pathlib import Path

from minio import Minio
from minio.error import S3Error

from backend.config import (
    MINIO_ACCESS_KEY,
    MINIO_BUCKET,
    MINIO_ENDPOINT,
    MINIO_SECRET_KEY,
    MINIO_SECURE,
)


class FileStorage:
    def __init__(self) -> None:
        self.client = Minio(
            MINIO_ENDPOINT,
            access_key=MINIO_ACCESS_KEY,
            secret_key=MINIO_SECRET_KEY,
            secure=MINIO_SECURE,
        )
        self.bucket = MINIO_BUCKET
        self._ensure_bucket()

    def _ensure_bucket(self) -> None:
        for attempt in range(30):
            try:
                if not self.client.bucket_exists(self.bucket):
                    self.client.make_bucket(self.bucket)
                return
            except S3Error:
                if attempt == 29:
                    raise
                time.sleep(1)

    def upload(self, object_key: str, data: bytes, content_type: str) -> None:
        self.client.put_object(
            self.bucket,
            object_key,
            io.BytesIO(data),
            length=len(data),
            content_type=content_type,
        )

    def download_bytes(self, object_key: str) -> bytes:
        response = self.client.get_object(self.bucket, object_key)
        try:
            return response.read()
        finally:
            response.close()
            response.release_conn()

    def download_to_path(self, object_key: str, dest: Path) -> None:
        dest.parent.mkdir(parents=True, exist_ok=True)
        self.client.fget_object(self.bucket, object_key, str(dest))

    def delete(self, object_key: str) -> None:
        try:
            self.client.remove_object(self.bucket, object_key)
        except S3Error:
            pass


_storage: FileStorage | None = None


def get_storage() -> FileStorage:
    global _storage
    if _storage is None:
        _storage = FileStorage()
    return _storage
