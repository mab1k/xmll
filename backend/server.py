"""FastAPI-сервер для веб-интерфейса генератора заключения."""
from __future__ import annotations

import io
import json
import shutil
import tempfile
import zipfile
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, File, Form, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.attempts_service import (
    create_attempt,
    delete_attempt,
    download_last_archive,
    generate_attempt_zip,
    get_attempt,
    get_stored_file,
    list_attempts,
    update_attempt,
)
from backend.auth import create_access_token, get_current_user, require_env_admin, user_to_dict
from backend.conclusion_builder import ValidationError, render_conclusion_xml_string
from backend.downloads import attachment_disposition
from backend.db import get_db, init_db
from backend.demo import generate_demo_zip, get_demo_file_response, get_demo_form
from backend.metadata import get_all_options
from backend.models import User
from backend.users_service import authenticate, create_user, delete_user, list_users, update_user


@asynccontextmanager
async def lifespan(_: FastAPI):
    from backend.storage import get_storage

    init_db()
    get_storage()
    yield


app = FastAPI(title="Генератор заключения экспертизы", version="1.2.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class LoginRequest(BaseModel):
    username: str
    password: str


class CreateUserRequest(BaseModel):
    username: str
    password: str


class UpdateUserRequest(BaseModel):
    username: str | None = None
    password: str | None = None
    isActive: bool | None = None


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/auth/login")
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate(db, body.username, body.password)
    token = create_access_token(user)
    return {"token": token, "user": user_to_dict(user)}


@app.get("/api/auth/me")
def me(user: User = Depends(get_current_user)):
    return user_to_dict(user)


@app.get("/api/options")
def options(_: User = Depends(get_current_user)):
    return get_all_options()


@app.get("/api/demo/form")
def demo_form(_: User = Depends(get_current_user)):
    return get_demo_form()


@app.get("/api/demo/files/{file_name}")
def demo_file(file_name: str, _: User = Depends(get_current_user)):
    return get_demo_file_response(file_name)


@app.post("/api/demo/generate")
def demo_generate(_: User = Depends(get_current_user)):
    return generate_demo_zip()


@app.get("/api/attempts")
def attempts_list(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    search: str = Query("", max_length=200),
    cadastral: str = Query("", max_length=200),
    egrz_number: str = Query("", max_length=200, alias="egrzNumber"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50, alias="pageSize"),
):
    return list_attempts(
        db,
        user,
        search=search,
        cadastral=cadastral,
        egrz_number=egrz_number,
        page=page,
        page_size=page_size,
    )


@app.post("/api/attempts")
async def attempts_create(
    payload: str = Form(...),
    title: str = Form(""),
    file_refs: str = Form("[]"),
    files: list[UploadFile] | None = File(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        form_data = json.loads(payload)
        refs = json.loads(file_refs)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail="Некорректный JSON") from exc
    return create_attempt(
        db,
        user=user,
        title=title,
        form_data=form_data,
        uploads=files or [],
        file_refs=refs,
    )


@app.get("/api/attempts/{attempt_id}")
def attempts_get(
    attempt_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return get_attempt(db, attempt_id, user)


@app.put("/api/attempts/{attempt_id}")
async def attempts_update(
    attempt_id: str,
    payload: str = Form(...),
    title: str = Form(""),
    file_refs: str = Form("[]"),
    files: list[UploadFile] | None = File(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        form_data = json.loads(payload)
        refs = json.loads(file_refs)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail="Некорректный JSON") from exc
    return update_attempt(
        db,
        attempt_id,
        user=user,
        title=title,
        form_data=form_data,
        uploads=files or [],
        file_refs=refs,
    )


@app.delete("/api/attempts/{attempt_id}")
def attempts_delete(
    attempt_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    delete_attempt(db, attempt_id, user)
    return {"ok": True}


@app.post("/api/attempts/{attempt_id}/generate")
def attempts_generate(
    attempt_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    buffer = generate_attempt_zip(db, attempt_id, user)
    return StreamingResponse(
        buffer,
        media_type="application/zip",
        headers={"Content-Disposition": attachment_disposition("conclusion.zip")},
    )


@app.get("/api/attempts/{attempt_id}/archive")
def attempts_download_archive(
    attempt_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    content, filename = download_last_archive(db, attempt_id, user)
    return Response(
        content=content,
        media_type="application/zip",
        headers={"Content-Disposition": attachment_disposition(filename)},
    )


@app.get("/api/files/{file_id}")
def files_download(
    file_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    stored, content = get_stored_file(db, file_id, user)
    return Response(
        content=content,
        media_type=stored.content_type,
        headers={"Content-Disposition": attachment_disposition(stored.original_name)},
    )


@app.post("/api/generate")
async def generate(
    payload: str = Form(...),
    files: list[UploadFile] | None = File(None),
    _: User = Depends(get_current_user),
):
    try:
        data = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail="Некорректный JSON в поле payload") from exc

    with tempfile.TemporaryDirectory() as tmp:
        upload_dir = Path(tmp)
        for upload in files or []:
            if not upload.filename:
                continue
            safe_name = Path(upload.filename).name
            dest = upload_dir / safe_name
            with dest.open("wb") as out:
                shutil.copyfileobj(upload.file, out)

        try:
            xml_text, output_files = render_conclusion_xml_string(data, upload_dir)
        except ValidationError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        buffer = io.BytesIO()
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
        return StreamingResponse(
            buffer,
            media_type="application/zip",
            headers={"Content-Disposition": attachment_disposition("conclusion.zip")},
        )


@app.get("/api/admin/users")
def admin_list_users(
    db: Session = Depends(get_db),
    _: User = Depends(require_env_admin),
):
    return list_users(db)


@app.post("/api/admin/users")
def admin_create_user(
    body: CreateUserRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_env_admin),
):
    return create_user(db, username=body.username, password=body.password)


@app.put("/api/admin/users/{user_id}")
def admin_update_user(
    user_id: str,
    body: UpdateUserRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(require_env_admin),
):
    return update_user(
        db,
        user_id,
        username=body.username,
        password=body.password,
        is_active=body.isActive,
        current_admin=admin,
    )


@app.delete("/api/admin/users/{user_id}")
def admin_delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(require_env_admin),
):
    delete_user(db, user_id, current_admin=admin)
    return {"ok": True}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.server:app", host="127.0.0.1", port=8000, reload=True)
