"""Сервис сохранённых попыток генерации."""
from __future__ import annotations

import json
import mimetypes
import shutil
import tempfile
import uuid
import zipfile
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path

from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from backend.conclusion_builder import ValidationError, render_conclusion_xml_string
from backend.form_payload import form_to_builder_payload
from backend.models import Attempt, StoredFile, User
from backend.storage import get_storage


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _guess_content_type(name: str) -> str:
    guessed, _ = mimetypes.guess_type(name)
    return guessed or "application/octet-stream"


def _default_title(form_data: dict) -> str:
    name = (form_data.get("examinationObject") or {}).get("name", "").strip()
    if name:
        return name
    return "Без названия"


def _file_map(attempt: Attempt) -> dict[str, StoredFile]:
    return {item.id: item for item in attempt.files}


def _attempt_meta(row: Attempt, form: dict | None = None) -> dict:
    if form is None:
        form = json.loads(row.form_data)
    return {
        "lastGeneratedAt": row.last_generated_at.isoformat() if row.last_generated_at else None,
        "hasArchive": bool(row.last_archive_key),
        "examinationObjectName": (form.get("examinationObject") or {}).get("name", ""),
    }


def _get_attempt(db: Session, attempt_id: str) -> Attempt:
    row = db.get(Attempt, attempt_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Попытка не найдена")
    return row


def list_attempts(
    db: Session,
    _user: User,
    *,
    search: str = "",
    page: int = 1,
    page_size: int = 10,
) -> dict:
    page = max(page, 1)
    page_size = min(max(page_size, 1), 50)

    query = db.query(Attempt)
    search_value = search.strip()
    if search_value:
        query = query.filter(Attempt.title.ilike(f"%{search_value}%"))

    total = query.count()
    rows = (
        query.order_by(Attempt.updated_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    items = []
    for row in rows:
        form = json.loads(row.form_data)
        items.append({
            "id": row.id,
            "title": row.title,
            "createdAt": row.created_at.isoformat(),
            "updatedAt": row.updated_at.isoformat(),
            **_attempt_meta(row, form),
        })

    total_pages = max((total + page_size - 1) // page_size, 1) if total else 0
    return {
        "items": items,
        "total": total,
        "page": page,
        "pageSize": page_size,
        "totalPages": total_pages,
    }


def get_attempt(db: Session, attempt_id: str, _user: User) -> dict:
    row = _get_attempt(db, attempt_id)
    form = json.loads(row.form_data)
    return {
        "id": row.id,
        "title": row.title,
        "form": form,
        "createdAt": row.created_at.isoformat(),
        "updatedAt": row.updated_at.isoformat(),
        **_attempt_meta(row, form),
    }


_ATTACHMENT_CATEGORIES = ("localConclusion", "registryCrypto", "contract", "workActs")


def _attachment_lookup(form_data: dict) -> dict[str, dict[str, dict]]:
    attachments = form_data.get("projectAttachments") or {}
    lookup: dict[str, dict[str, dict]] = {}
    for category in _ATTACHMENT_CATEGORIES:
        lookup[category] = {
            item["id"]: item
            for item in attachments.get(category, [])
            if item.get("id")
        }
    return lookup


def _store_upload(
    db: Session,
    attempt: Attempt,
    upload: UploadFile,
    files_by_id: dict[str, StoredFile],
) -> StoredFile:
    content = upload.file.read()
    stored_id = str(uuid.uuid4())
    object_key = f"{attempt.id}/{stored_id}/{Path(upload.filename).name}"
    get_storage().upload(object_key, content, _guess_content_type(upload.filename))

    stored = StoredFile(
        id=stored_id,
        attempt_id=attempt.id,
        original_name=Path(upload.filename).name,
        content_type=_guess_content_type(upload.filename),
        object_key=object_key,
    )
    db.add(stored)
    files_by_id[stored_id] = stored
    return stored


def _replace_stored_file(
    files_by_id: dict[str, StoredFile],
    db: Session,
    old_id: str | None,
) -> None:
    if old_id and old_id in files_by_id:
        old = files_by_id.pop(old_id)
        get_storage().delete(old.object_key)
        db.delete(old)


def _apply_uploads(
    db: Session,
    attempt: Attempt,
    form_data: dict,
    uploads: list[UploadFile],
    file_refs: list[dict],
) -> None:
    documents = {doc["id"]: doc for doc in form_data.get("documents", []) if doc.get("id")}
    attachments = _attachment_lookup(form_data)
    files_by_id = _file_map(attempt)

    for upload, ref in zip(uploads, file_refs, strict=False):
        if not upload.filename:
            continue
        kind = ref.get("kind")

        if kind == "attachment":
            category = ref.get("attachmentCategory")
            attachment_id = ref.get("attachmentId")
            if category not in attachments or attachment_id not in attachments[category]:
                continue
            item = attachments[category][attachment_id]
            stored = _store_upload(db, attempt, upload, files_by_id)
            _replace_stored_file(files_by_id, db, item.get("fileStorageId"))
            item["fileStorageId"] = stored.id
            item["fileName"] = stored.original_name
            continue

        doc_id = ref.get("docId")
        if doc_id not in documents:
            continue

        doc = documents[doc_id]
        stored = _store_upload(db, attempt, upload, files_by_id)

        if kind == "file":
            _replace_stored_file(files_by_id, db, doc.get("fileStorageId"))
            doc["fileStorageId"] = stored.id
            doc["fileName"] = stored.original_name
        elif kind == "sign":
            index = int(ref.get("index", 0))
            sign_ids = list(doc.get("signStorageIds") or [])
            sign_names = list(doc.get("signFileNames") or [])
            while len(sign_ids) <= index:
                sign_ids.append("")
            while len(sign_names) <= index:
                sign_names.append("")
            old_id = sign_ids[index] if index < len(sign_ids) else ""
            _replace_stored_file(files_by_id, db, old_id)
            sign_ids[index] = stored.id
            sign_names[index] = stored.original_name
            doc["signStorageIds"] = sign_ids
            doc["signFileNames"] = sign_names


def create_attempt(
    db: Session,
    *,
    user: User,
    title: str | None,
    form_data: dict,
    uploads: list[UploadFile],
    file_refs: list[dict],
) -> dict:
    attempt = Attempt(
        user_id=user.id,
        title=(title or "").strip() or _default_title(form_data),
        form_data=json.dumps(form_data, ensure_ascii=False),
    )
    db.add(attempt)
    db.flush()
    _apply_uploads(db, attempt, form_data, uploads, file_refs)
    attempt.form_data = json.dumps(form_data, ensure_ascii=False)
    attempt.updated_at = _utcnow()
    db.commit()
    db.refresh(attempt)
    return get_attempt(db, attempt.id, user)


def update_attempt(
    db: Session,
    attempt_id: str,
    *,
    user: User,
    title: str | None,
    form_data: dict,
    uploads: list[UploadFile],
    file_refs: list[dict],
) -> dict:
    attempt = _get_attempt(db, attempt_id)

    if title is not None and title.strip():
        attempt.title = title.strip()
    _apply_uploads(db, attempt, form_data, uploads, file_refs)
    attempt.form_data = json.dumps(form_data, ensure_ascii=False)
    attempt.updated_at = _utcnow()
    _clear_last_archive(attempt)
    db.commit()
    db.refresh(attempt)
    return get_attempt(db, attempt.id, user)


def _clear_last_archive(attempt: Attempt) -> None:
    if attempt.last_archive_key:
        get_storage().delete(attempt.last_archive_key)
        attempt.last_archive_key = None
        attempt.last_generated_at = None


def delete_attempt(db: Session, attempt_id: str, _user: User) -> None:
    attempt = _get_attempt(db, attempt_id)
    for item in attempt.files:
        get_storage().delete(item.object_key)
    _clear_last_archive(attempt)
    db.delete(attempt)
    db.commit()


def get_stored_file(db: Session, file_id: str, _user: User) -> tuple[StoredFile, bytes]:
    row = db.get(StoredFile, file_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Файл не найден")
    return row, get_storage().download_bytes(row.object_key)


def _build_attempt_zip(attempt: Attempt) -> BytesIO:
    form_data = json.loads(attempt.form_data)
    files_by_id = _file_map(attempt)

    with tempfile.TemporaryDirectory() as tmp:
        upload_dir = Path(tmp)
        for doc in form_data.get("documents", []):
            file_id = doc.get("fileStorageId")
            if file_id and file_id in files_by_id:
                item = files_by_id[file_id]
                get_storage().download_to_path(item.object_key, upload_dir / item.original_name)
            for sign_id in doc.get("signStorageIds") or []:
                if sign_id and sign_id in files_by_id:
                    item = files_by_id[sign_id]
                    get_storage().download_to_path(item.object_key, upload_dir / item.original_name)

        payload = form_to_builder_payload(form_data, files_by_id)
        try:
            xml_text, output_files = render_conclusion_xml_string(payload, upload_dir)
        except ValidationError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        buffer = BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("conclusion.xml", xml_text.encode("utf-8"))
            seen = set()
            for file_path in output_files:
                path = Path(file_path)
                if path.name in seen:
                    continue
                seen.add(path.name)
                archive.write(path, arcname=path.name)
        buffer.seek(0)
        return buffer


def generate_attempt_zip(db: Session, attempt_id: str, _user: User) -> BytesIO:
    attempt = _get_attempt(db, attempt_id)

    buffer = _build_attempt_zip(attempt)
    archive_key = f"{attempt.id}/generated/conclusion.zip"
    _clear_last_archive(attempt)
    get_storage().upload(archive_key, buffer.getvalue(), "application/zip")
    attempt.last_archive_key = archive_key
    attempt.last_generated_at = _utcnow()
    db.commit()
    buffer.seek(0)
    return buffer


def download_last_archive(db: Session, attempt_id: str, _user: User) -> tuple[bytes, str]:
    attempt = _get_attempt(db, attempt_id)
    if not attempt.last_archive_key:
        raise HTTPException(status_code=404, detail="Архив ещё не создавался. Сначала нажмите «Создать XML».")
    content = get_storage().download_bytes(attempt.last_archive_key)
    return content, "conclusion.zip"
