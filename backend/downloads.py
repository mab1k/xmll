"""Заголовки для скачивания файлов с поддержкой кириллицы в имени."""
from __future__ import annotations

from urllib.parse import quote


def attachment_disposition(filename: str) -> str:
    ascii_fallback = "".join(c if ord(c) < 128 else "_" for c in filename) or "download"
    encoded = quote(filename)
    return f"attachment; filename=\"{ascii_fallback}\"; filename*=UTF-8''{encoded}"
