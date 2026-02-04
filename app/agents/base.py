from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Literal, Optional, TypedDict


NextAgent = Literal["intent", "retrieval", "tool", "final", "safety", "stop"]


class AgentResult(TypedDict, total=False):
    agent: str
    status: Literal["ok", "error"]
    data: Dict[str, Any]
    confidence: float
    next: List[NextAgent]
    error: str


class BaseAgent(ABC):
    name: str

    @abstractmethod
    def run(self, state: Dict[str, Any]) -> AgentResult:
        raise NotImplementedError
