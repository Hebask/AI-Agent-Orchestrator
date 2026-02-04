from __future__ import annotations

from typing import Any, Dict, List, Optional

from pypdf import PdfReader

from app.core.config import settings
from app.core.db import get_store
from app.core.ollama_client import OllamaClient


def extract_pdf_text(file_path: str, max_pages: Optional[int] = None) -> str:
    """
    Extract text from a PDF.
    Note: scanned PDFs may return empty text (no OCR in this project).
    """
    reader = PdfReader(file_path)
    pages: List[str] = []

    total_pages = len(reader.pages)
    limit = min(total_pages, max_pages) if max_pages else total_pages

    for i in range(limit):
        t = reader.pages[i].extract_text() or ""
        # normalize nulls / weird whitespace a bit
        pages.append(t.replace("\x00", " "))

    return "\n".join(pages).strip()


def chunk_text(text: str, chunk_size: int = 1200, overlap: int = 200, max_chunks: int = 500) -> List[str]:
    """
    Simple sliding window chunking with overlap.
    max_chunks prevents huge PDFs from producing thousands of chunks.
    """
    if not text:
        return []

    chunk_size = max(200, int(chunk_size))
    overlap = max(0, min(int(overlap), chunk_size - 1))
    step = max(1, chunk_size - overlap)

    chunks: List[str] = []
    i = 0
    while i < len(text) and len(chunks) < max_chunks:
        chunk = text[i : i + chunk_size].strip()
        if chunk:
            chunks.append(chunk)
        i += step

    return chunks


def ingest_pdf(
    *,
    user_id: str,
    file_path: str,
    filename: str,
    content_type: str,
    compute_embeddings: Optional[bool] = None,
) -> Dict[str, Any]:
    """
    Ingest a PDF:
    - create file record
    - extract text
    - chunk
    - (optional) embed
    - store chunks
    """
    compute_embeddings = settings.enable_embeddings if compute_embeddings is None else compute_embeddings

    store = get_store()
    file_id = store.create_file(user_id=user_id, filename=filename, content_type=content_type)

    # Safety caps (tune as you like)
    max_pages = getattr(settings, "max_pdf_pages", 200)
    max_text_chars = getattr(settings, "max_pdf_text_chars", 2_000_000)  # 2M chars
    max_chunks = getattr(settings, "max_pdf_chunks", 800)

    text = extract_pdf_text(file_path, max_pages=max_pages)

    if not text:
        # This happens for scanned PDFs (no OCR).
        return {
            "ok": True,
            "file_id": file_id,
            "filename": filename,
            "chunks": 0,
            "warning": "No extractable text found in PDF (scanned image PDF). OCR is not enabled.",
        }

    # clamp huge extracted text
    if len(text) > max_text_chars:
        text = text[:max_text_chars]

    chunks = chunk_text(
        text,
        chunk_size=getattr(settings, "chunk_size", 1200),
        overlap=getattr(settings, "chunk_overlap", 200),
        max_chunks=max_chunks,
    )

    client: Optional[OllamaClient] = None
    if compute_embeddings:
        client = OllamaClient(settings.ollama_base_url, settings.embed_model, timeout=settings.ollama_timeout_sec)

    for idx, chunk in enumerate(chunks):
        emb = None
        if compute_embeddings and client:
            # Keep embedding input bounded
            safe = chunk[:2000]
            try:
                emb = client.embeddings(safe, model=settings.embed_model)
            except Exception:
                emb = None

        store.add_chunk(
            user_id=user_id,
            file_id=file_id,
            filename=filename,
            chunk_index=idx,
            content=chunk,
            embedding=emb,
        )

    return {"ok": True, "file_id": file_id, "filename": filename, "chunks": len(chunks)}
