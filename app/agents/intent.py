from __future__ import annotations

import json
from typing import Any, Dict

from app.agents.base import BaseAgent, AgentResult
from app.core.config import settings
from app.core.ollama_client import OllamaClient


class IntentAgent(BaseAgent):
    name = "intent"

    def __init__(self) -> None:
        self.client = OllamaClient(settings.ollama_base_url, settings.ollama_model, timeout=settings.ollama_timeout_sec)

    def run(self, state: Dict[str, Any]) -> AgentResult:
        user_message = (state.get("input") or "").strip()

        system_prompt = (
            "You are an Intent Classification Agent. Return ONLY valid JSON.\n"
            "Your job: decide whether to call retrieval, tool, or go straight to final.\n\n"
            "Rules:\n"
            "- needs_tools=true for calculations, arithmetic, unit conversions, or getting current time.\n"
            "- needs_retrieval=true when the question likely needs information from uploaded files or past chat history.\n"
            "- If the user asks about an uploaded document, set needs_retrieval=true.\n\n"
            "Schema (strict):\n"
            "{\n"
            "  \"intent\": \"question|action|lookup|chat\",\n"
            "  \"needs_retrieval\": true|false,\n"
            "  \"needs_tools\": true|false,\n"
            "  \"notes\": \"short reason\",\n"
            "  \"confidence\": 0.0-1.0\n"
            "}\n"
        )

        raw = self.client.chat(
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_message}],
            response_format="json",
        )

        try:
            data = json.loads(raw)
        except Exception:
            # fallback: default to final
            data = {"intent": "question", "needs_retrieval": False, "needs_tools": False, "notes": "parse_failed", "confidence": 0.4}

        state["intent"] = data

        nxt = []
        if data.get("needs_tools") is True:
            nxt.append("tool")
        if data.get("needs_retrieval") is True:
            nxt.append("retrieval")
        if not nxt:
            nxt = ["final"]

        return AgentResult(agent=self.name, status="ok", data=data, confidence=float(data.get("confidence", 0.7)), next=nxt)
