from __future__ import annotations
from typing import Optional
from app.core.config import settings
from app.repositories.base import Store

_store: Optional[Store] = None

def get_store() -> Store:
    global _store
    if _store is not None:
        return _store

    if settings.require_mongo and not settings.mongo_uri:
        raise RuntimeError("MongoDB is required but MONGO_URI is not set.")

    if settings.mongo_uri:
        from app.repositories.mongo_store import MongoStore
        _store = MongoStore(settings.mongo_uri, settings.mongo_db)
        return _store

    from app.repositories.local_json_store import LocalJsonStore
    _store = LocalJsonStore(base_dir=settings.storage_dir)
    return _store
