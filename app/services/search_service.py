from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.core.config import settings
from app.core.ollama_client import OllamaClient
from app.core.db import get_store

def search(user_id: str, query: str, limit: int = 5):
    store = get_store()
    return store.search_chunks(user_id=user_id, query=query, limit=limit)

