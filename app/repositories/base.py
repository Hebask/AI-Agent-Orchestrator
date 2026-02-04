from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class Store(ABC):
    """Storage abstraction. Implemented by MongoStore and LocalJsonStore."""

    @abstractmethod
    def append_chat(self, user_id: str, role: str, text: str, meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def get_recent_chats(self, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def create_file(self, user_id: str, filename: str, content_type: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def add_chunk(
        self,
        user_id: str,
        file_id: str,
        filename: str,
        chunk_index: int,
        content: str,
        embedding: Optional[List[float]] = None,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def search(
        self,
        user_id: str,
        query: str,
        top_k: int = 5,
        query_embedding: Optional[List[float]] = None,
    ) -> List[Dict[str, Any]]:
        raise NotImplementedError
