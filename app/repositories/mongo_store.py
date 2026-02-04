from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.errors import OperationFailure

from .base import Store


class MongoStore(Store):
    def __init__(self, mongo_uri: str, db_name: str):
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]

        self.chats: Collection = self.db["chats"]
        self.files: Collection = self.db["files"]
        self.chunks: Collection = self.db["file_chunks"]

        # ---- non-text indexes (safe to create repeatedly) ----
        self.chats.create_index([("user_id", 1), ("created_at", -1)])
        self.files.create_index([("user_id", 1), ("created_at", -1)])
        self.chunks.create_index([("user_id", 1), ("file_id", 1), ("chunk_index", 1)])

        # ---- text indexes (Mongo allows ONLY one text index per collection) ----
        # chats: ensure text index exists on "text"
        self._ensure_single_text_index(self.chats, preferred_field="text")

        # chunks: ensure text index exists (prefer "text" for maximum compatibility)
        # NOTE: we store chunk content into BOTH "content" and "text" fields.
        # If an old Atlas index exists on "text", searches will still work.
        self._ensure_single_text_index(self.chunks, preferred_field="text")

    def _ensure_single_text_index(self, collection: Collection, preferred_field: str = "text") -> None:
        """
        MongoDB allows only ONE text index per collection.
        If a text index already exists (any name/field/options), do nothing.
        If none exists, create it on preferred_field.
        """
        try:
            for ix in collection.list_indexes():
                # text indexes include "weights"
                if "weights" in ix:
                    return

            collection.create_index([(preferred_field, "text")], name=f"{preferred_field}_text_idx")

        except OperationFailure as e:
            msg = str(e)
            # Accept "already exists" / "IndexOptionsConflict" and continue
            if "IndexOptionsConflict" in msg or "already exists" in msg:
                return
            raise

        # -------------------- workflow runs --------------------

    def create_run(self, user_id: str, input_text: str) -> str:
        import uuid

        run_id = str(uuid.uuid4())
        self.db["workflow_runs"].insert_one(
            {
                "run_id": run_id,
                "user_id": user_id,
                "input": input_text,
                "steps": [],
                "status": "running",
                "created_at": datetime.utcnow(),
            }
        )
        return run_id

    def append_run_step(self, run_id: str, agent: str, output: dict) -> None:
        self.db["workflow_runs"].update_one(
            {"run_id": run_id},
            {"$push": {"steps": {"agent": agent, "output": output}}},
        )

    def finalize_run(self, run_id: str, final_reply: str, agent_path: list[str], confidence: float) -> None:
        self.db["workflow_runs"].update_one(
            {"run_id": run_id},
            {
                "$set": {
                    "final_reply": final_reply,
                    "agent_path": agent_path,
                    "confidence": confidence,
                    "status": "completed",
                    "completed_at": datetime.utcnow(),
                }
            },
        )

    def get_run(self, run_id: str) -> dict | None:
        return self.db["workflow_runs"].find_one({"run_id": run_id}, {"_id": 0})

    def list_runs(self, user_id: str, limit: int = 20) -> list[dict]:
        return list(
            self.db["workflow_runs"]
            .find({"user_id": user_id}, {"_id": 0})
            .sort("created_at", -1)
            .limit(limit)
        )

    # -------------------- chats --------------------

    def append_chat(
        self,
        user_id: str,
        role: str,
        text: str,
        meta: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        doc = {
            "user_id": user_id,
            "role": role,
            "text": text,
            "meta": meta or {},
            "created_at": datetime.utcnow(),
        }
        self.chats.insert_one(doc)
        doc.pop("_id", None)
        return doc

    def get_recent_chats(self, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        return list(self.chats.find({"user_id": user_id}, {"_id": 0}).sort("created_at", -1).limit(limit))

    # -------------------- files + chunks --------------------

    def create_file(self, user_id: str, filename: str, content_type: str) -> str:
        import uuid

        file_id = str(uuid.uuid4())
        self.files.insert_one(
            {
                "user_id": user_id,
                "file_id": file_id,
                "filename": filename,
                "content_type": content_type,
                "created_at": datetime.utcnow(),
            }
        )
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
        # Store content in BOTH fields to support existing Atlas indexes (often on "text").
        self.chunks.insert_one(
            {
                "user_id": user_id,
                "file_id": file_id,
                "filename": filename,
                "chunk_index": int(chunk_index),
                "content": content,
                "text": content,  # ✅ critical for compatibility with existing "text_text" index
                "embedding": embedding,
                "created_at": datetime.utcnow(),
            }
        )

    # -------------------- search --------------------

    def search(
        self,
        user_id: str,
        query: str,
        top_k: int = 5,
        query_embedding: Optional[List[float]] = None,
    ) -> List[Dict[str, Any]]:
        """
        For now: Mongo $text search across file chunks + chats.
        (Embedding search can be added later.)
        """

        q = (query or "").strip()
        if not q:
            return []

        # file chunks
        hits = list(
            self.chunks.find(
                {"user_id": user_id, "$text": {"$search": q}},
                {
                    "_id": 0,
                    "score": {"$meta": "textScore"},
                    "content": 1,
                    "file_id": 1,
                    "filename": 1,
                    "chunk_index": 1,
                },
            )
            .sort([("score", {"$meta": "textScore"})])
            .limit(int(top_k))
        )

        results: List[Dict[str, Any]] = []
        for h in hits:
            results.append(
                {
                    "source_type": "file",
                    "source": h.get("filename", h.get("file_id", "unknown")),
                    "file_id": h.get("file_id"),
                    "chunk_index": h.get("chunk_index"),
                    "score": float(h.get("score", 0.0)),
                    "snippet": (h.get("content") or "")[:800].replace("\n", " ").strip(),
                }
            )

        # chats (fill remaining slots)
        remaining = max(0, int(top_k) - len(results))
        if remaining > 0:
            chat_hits = list(
                self.chats.find(
                    {"user_id": user_id, "$text": {"$search": q}},
                    {"_id": 0, "score": {"$meta": "textScore"}, "text": 1, "created_at": 1},
                )
                .sort([("score", {"$meta": "textScore"})])
                .limit(remaining)
            )
            for h in chat_hits:
                results.append(
                    {
                        "source_type": "chat",
                        "source": "chat_history",
                        "score": float(h.get("score", 0.0)),
                        "snippet": (h.get("text") or "")[:800].replace("\n", " ").strip(),
                        "created_at": (h.get("created_at").isoformat() + "Z") if h.get("created_at") else None,
                    }
                )

        return results
