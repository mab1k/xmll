"""Демо-данные и генерация примера conclusion.xml."""
from __future__ import annotations

import io
import shutil
import tempfile
import zipfile
from pathlib import Path

from fastapi import HTTPException
from fastapi.responses import FileResponse, StreamingResponse

from backend.conclusion_builder import ValidationError, render_conclusion_xml_string
from backend.xml_to_payload import load_payload_from_xml

DATA_DIR = Path(__file__).resolve().parent / "data"
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEMO_FILES = frozenset({"2.pdf", "1774366449_3.pdf", "demo.pdf"})


def _find_demo_xml() -> Path:
    for path in (
        DATA_DIR / "conclusion.xml",
        PROJECT_ROOT / "conclusion.xml",
    ):
        if path.is_file():
            return path
    raise HTTPException(status_code=404, detail="Демо-файл conclusion.xml не найден")


def _find_demo_file(file_name: str) -> Path:
    safe_name = Path(file_name).name
    if safe_name not in DEMO_FILES:
        raise HTTPException(status_code=404, detail="Файл не найден")
    candidates = [DATA_DIR / safe_name, PROJECT_ROOT / safe_name]
    if safe_name != "demo.pdf":
        candidates.append(DATA_DIR / "demo.pdf")
    for path in candidates:
        if path.is_file():
            return path
    raise HTTPException(status_code=404, detail="Демо-файл не найден на сервере")


def get_demo_form() -> dict:
    return load_payload_from_xml(_find_demo_xml())


def get_demo_file_response(file_name: str) -> FileResponse:
    path = _find_demo_file(file_name)
    media_type = "application/pdf" if path.suffix.lower() == ".pdf" else "application/octet-stream"
    return FileResponse(path, filename=path.name, media_type=media_type)


def generate_demo_zip() -> StreamingResponse:
    payload = get_demo_form()
    unique_names = {
        (doc.get("fileName") or "").strip()
        for doc in payload.get("documents", [])
        if (doc.get("fileName") or "").strip()
    }

    with tempfile.TemporaryDirectory() as tmp:
        upload_dir = Path(tmp)
        for name in unique_names:
            source = _find_demo_file(name)
            shutil.copy2(source, upload_dir / name)

        try:
            xml_text, output_files = render_conclusion_xml_string(payload, upload_dir)
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
        headers={"Content-Disposition": 'attachment; filename="conclusion-demo.zip"'},
    )
