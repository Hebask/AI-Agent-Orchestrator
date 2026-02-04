from __future__ import annotations

from typing import Any, Dict, List

from app.agents.intent import IntentAgent
from app.agents.retrieval import RetrievalAgent
from app.agents.tool import ToolAgent
from app.agents.safety import SafetyAgent
from app.agents.final_builder import FinalBuilderAgent
from app.core.config import settings


class OrchestratorService:
    """Central controller that routes the request through agents with a hop limit."""

    def __init__(self, max_hops: int | None = None):
        self.max_hops = max_hops or settings.max_hops
        self.agents = {
            "intent": IntentAgent(),
            "retrieval": RetrievalAgent(),
            "tool": ToolAgent(),
            "final": FinalBuilderAgent(),
            "safety": SafetyAgent(),
        }

    def run(self, user_message: str, user_id: str = "default") -> Dict[str, Any]:
        state: Dict[str, Any] = {
            "user_id": user_id,
            "input": user_message,
            "agent_path": [],
            "intent": {},
            "retrieval_hits": [],
            "tool_result": None,
            "draft_reply": "",
            "confidence": 0.5,
        }

        queue: List[str] = ["intent"]
        hops = 0

        while queue and hops < self.max_hops:
            current = queue.pop(0)
            if current not in self.agents:
                break

            result = self.agents[current].run(state)
            state["agent_path"].append(current)

            nxt = result.get("next") or []
            # Normalize: allow 'stop'
            nxt = [n for n in nxt if n != "stop"]

            # Safety always ends
            if current == "safety":
                break

            # Extend queue (avoid duplicates)
            for n in nxt:
                if n in self.agents and n not in queue:
                    queue.append(n)

            hops += 1

        # Output contract
        reply = state.get("draft_reply") or ""
        confidence = float(state.get("confidence", 0.6))
        return {
            "reply": reply,
            "agent_path": state.get("agent_path", []),
            "confidence": max(0.0, min(1.0, confidence)),
        }
