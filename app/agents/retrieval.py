from __future__ import annotations

from typing import Any, Dict

from app.agents.base import BaseAgent, AgentResult
from app.core.config import settings
from app.services.search_service import search


class RetrievalAgent(BaseAgent):
    name = "retrieval"

    def run(self, state: Dict[str, Any]) -> AgentResult:
        query = state.get("input", "") or ""
        user_id = state.get("user_id", "default")

        hits = search(user_id=user_id, query=query, top_k=settings.top_k)
        state["retrieval_hits"] = hits

        confidence = 0.85 if hits else 0.45
        return AgentResult(agent=self.name, status="ok", data={"hits": hits}, confidence=confidence, next=["final"])
