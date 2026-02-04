from __future__ import annotations

from typing import Any, Dict, List, Optional
from app.core.db import get_store

def append_message(user_id: str, role: str, text: str, meta=None):
    store = get_store()
    return store.append_chat(user_id=user_id, role=role, text=text, meta=meta)

def recent_messages(user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
    return store.get_recent_chats(user_id=user_id, limit=limit)
