from __future__ import annotations

from app.core.db import get_store

def search(user_id: str, query: str, top_k: int = 5):
    store = get_store()
    return store.search(user_id=user_id, query=query, top_k=top_k)
