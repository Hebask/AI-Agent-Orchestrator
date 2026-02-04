from __future__ import annotations

import json
import os
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from .base import Store


def _now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"


class LocalJsonStore(Store):
    """File-based storage (storage/index.json, storage/chats.json). Good for demo/offline use."""

    def __init__(self, storage_dir: str):
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)
        self._chats_path = os.path.join(self.storage_dir, "chats.json")
        self._index_path = os.path.join(self.storage_dir, "index.json")

        if not os.path.exists(self._chats_path):
            with open(self._chats_path, "w", encoding="utf-8") as f:
                json.dump([], f)
        if not os.path.exists(self._index_path):
            with open(self._index_path, "w", encoding="utf-8") as f:
                json.dump({"files": [], "chunks": []}, f)

    def _read_json(self, path: str) -> Any:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write_json(self, path: str, obj: Any) -> None:
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False, indent=2)
        os.replace(tmp, path)

    def append_chat(self, user_id: str, role: str, text: str, meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        chats = self._read_json(self._chats_path)
        doc = {"user_id": user_id, "role": role, "text": text, "meta": meta or {}, "created_at": _now_iso()}
        chats.append(doc)
        self._write_json(self._chats_path, chats)
        return doc

    def get_recent_chats(self, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        chats = self._read_json(self._chats_path)
        user_chats = [c for c in chats if c.get("user_id") == user_id]
        return list(reversed(user_chats[-limit:]))

    def create_file(self, user_id: str, filename: str, content_type: str) -> str:
        idx = self._read_json(self._index_path)
        file_id = str(uuid.uuid4())
        idx["files"].append({"user_id": user_id, "file_id": file_id, "filename": filename, "content_type": content_type, "created_at": _now_iso()})
        self._write_json(self._index_path, idx)
        return file_id

    def add_chunk(
        self,
        user_id: str,
        file_id: str,
        filename: str,
        chunk_index: int,
        content: str,
        embedding: Optional[List[float]] = None,
    ) -> None:
        idx = self._read_json(self._index_path)
        idx["chunks"].append(
            {
                "user_id": user_id,
                "file_id": file_id,
                "filename": filename,
                "chunk_index": chunk_index,
                "content": content,
                "embedding": embedding,
            }
        )
        self._write_json(self._index_path, idx)

    def search(self, user_id: str, query: str, top_k: int = 5, query_embedding: Optional[List[float]] = None) -> List[Dict[str, Any]]:
        idx = self._read_json(self._index_path)
        chunks = [c for c in idx.get("chunks", []) if c.get("user_id") == user_id]
        q = (query or "").lower()

        def score_text(c: Dict[str, Any]) -> float:
            text = (c.get("content") or "").lower()
            if not q:
                return 0.0
            # simple term frequency score
            return sum(text.count(tok) for tok in q.split() if tok)

        scored = []
        for c in chunks:
            s = score_text(c)
            if s > 0:
                scored.append((s, c))
        scored.sort(key=lambda x: x[0], reverse=True)

        hits: List[Dict[str, Any]] = []
        for s, c in scored[:top_k]:
            hits.append(
                {
                    "source_type": "file",
                    "source": c.get("filename", c.get("file_id", "unknown")),
                    "file_id": c.get("file_id"),
                    "chunk_index": c.get("chunk_index"),
                    "score": float(s),
                    "snippet": (c.get("content") or "")[:800].replace("\n", " ").strip(),
                }
            )

        # also search chats
        chats = self._read_json(self._chats_path)
        user_chats = [c for c in chats if c.get("user_id") == user_id]
        chat_scored = []
        for c in user_chats:
            text = (c.get("text") or "").lower()
            s = sum(text.count(tok) for tok in q.split() if tok)
            if s > 0:
                chat_scored.append((s, c))
        chat_scored.sort(key=lambda x: x[0], reverse=True)

        for s, c in chat_scored[: max(0, top_k - len(hits))]:
            hits.append(
                {
                    "source_type": "chat",
                    "source": "chat_history",
                    "score": float(s),
                    "snippet": (c.get("text") or "")[:800].replace("\n", " ").strip(),
                    "created_at": c.get("created_at"),
                }
            )

        return hits
