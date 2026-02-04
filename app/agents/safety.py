from __future__ import annotations

import re
from typing import Any, Dict

from app.agents.base import BaseAgent, AgentResult


# Minimal demo block-list (extend for production)
BLOCK_PATTERNS = [
    r"\bhow to make a bomb\b",
    r"\bmake an? explosive\b",
    r"\bkill yourself\b",
    r"\bsuicide\b",
]


class SafetyAgent(BaseAgent):
    name = "safety"

    def run(self, state: Dict[str, Any]) -> AgentResult:
        draft = (state.get("draft_reply") or "").strip()
        flags = [p for p in BLOCK_PATTERNS if re.search(p, draft, re.IGNORECASE)]

        if flags:
            state["draft_reply"] = "I can’t help with that request. If you tell me the safe goal, I’ll help."
            state["confidence"] = 1.0
            return AgentResult(agent=self.name, status="ok", data={"blocked": True, "flags": flags}, confidence=1.0, next=["stop"])

        return AgentResult(agent=self.name, status="ok", data={"blocked": False}, confidence=1.0, next=["stop"])
