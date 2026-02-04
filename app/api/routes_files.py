from __future__ import annotations

import os
import uuid
from typing import List, Tuple

import aiofiles
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel

from app.core.config import settings
from app.services.ingestion_service import ingest_pdf

router = APIRouter(prefix="/files", tags=["files"])


class UploadResponse(BaseModel):
    ok: bool
    file_id: str
    filename: str
    chunks: int


class UploadErrorItem(BaseModel):
    ok: bool
    filename: str
    error: str


class UploadMultipleResponse(BaseModel):
    ok: bool
    items: List[UploadResponse]
    errors: List[UploadErrorItem]


def _ensure_pdf(filename: str) -> None:
    ext = os.path.splitext(filename)[1].lower()
    if ext != ".pdf":
        raise HTTPException(status_code=400, detail=f"Only PDF is supported (got {ext or 'no extension'})")


async def _save_pdf_to_disk(upload: UploadFile, files_dir: str, max_bytes: int) -> Tuple[str, str]:
    if not upload.filename:
        raise HTTPException(status_code=400, detail="Missing filename")

    _ensure_pdf(upload.filename)

    saved_name = f"{uuid.uuid4()}.pdf"
    saved_path = os.path.join(files_dir, saved_name)

    total = 0
    try:
        async with aiofiles.open(saved_path, "wb") as out:
            while True:
                chunk = await upload.read(1024 * 1024)  # 1MB
                if not chunk:
                    break
                total += len(chunk)
                if total > max_bytes:
                    raise HTTPException(
                        status_code=413,
                        detail=f"File too large. Max allowed is {max_bytes} bytes.",
                    )
                await out.write(chunk)
    except HTTPException:
        # re-raise HTTP errors (400/413 etc.)
        raise
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Failed saving file: {e}") from e
    finally:
        try:
            await upload.close()
        except Exception:
            pass

    return saved_path, upload.filename


@router.post("/upload", response_model=UploadResponse)
async def upload_file(user_id: str = "default", file: UploadFile = File(...)):
    storage_dir = settings.storage_dir
    files_dir = os.path.join(storage_dir, "files")
    os.makedirs(files_dir, exist_ok=True)

    # 25MB default (change in config if you want)
    max_bytes = getattr(settings, "max_upload_bytes", 25 * 1024 * 1024)

    saved_path, original_name = await _save_pdf_to_disk(file, files_dir, max_bytes=max_bytes)

    result = ingest_pdf(
        user_id=user_id,
        file_path=saved_path,
        filename=original_name,
        content_type="application/pdf",
    )
    return UploadResponse(**result)


@router.post("/upload-multiple", response_model=UploadMultipleResponse)
async def upload_multiple(user_id: str = "default", files: List[UploadFile] = File(...)):
    """
    Upload multiple PDFs in one request.

    Postman:
    Body -> form-data -> key "files" (type File) -> add multiple rows with same key.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    storage_dir = settings.storage_dir
    files_dir = os.path.join(storage_dir, "files")
    os.makedirs(files_dir, exist_ok=True)

    max_bytes = getattr(settings, "max_upload_bytes", 25 * 1024 * 1024)

    items: List[UploadResponse] = []
    errors: List[UploadErrorItem] = []

    for f in files:
        try:
            saved_path, original_name = await _save_pdf_to_disk(f, files_dir, max_bytes=max_bytes)
            result = ingest_pdf(
                user_id=user_id,
                file_path=saved_path,
                filename=original_name,
                content_type="application/pdf",
            )
            items.append(UploadResponse(**result))
        except HTTPException as e:
            # Per-file failure should not kill the whole batch
            errors.append(
                UploadErrorItem(ok=False, filename=getattr(f, "filename", "unknown") or "unknown", error=str(e.detail))
            )
        except Exception as e:  # noqa: BLE001
            errors.append(
                UploadErrorItem(ok=False, filename=getattr(f, "filename", "unknown") or "unknown", error=str(e))
            )

    return UploadMultipleResponse(ok=(len(errors) == 0), items=items, errors=errors)