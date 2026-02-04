from __future__ import annotations

import json
from typing import Any, Dict, List

from app.agents.base import BaseAgent, AgentResult
from app.core.config import settings
from app.core.ollama_client import OllamaClient


class FinalBuilderAgent(BaseAgent):
    name = "final"

    def __init__(self) -> None:
        self.client = OllamaClient(settings.ollama_base_url, settings.ollama_model, timeout=settings.ollama_timeout_sec)

    def run(self, state: Dict[str, Any]) -> AgentResult:
        user_input = state.get("input", "") or ""
        hits: List[Dict[str, Any]] = state.get("retrieval_hits") or []
        tool_payload = state.get("tool_result")
        intent = state.get("intent") or {}

        tool_context = ""
        if isinstance(tool_payload, dict):
            tool_context = json.dumps(tool_payload, ensure_ascii=False)

        evidence = []
        for h in hits[:8]:
            evidence.append(f"- ({h.get('source_type')}) {h.get('source')}: {h.get('snippet')}")
        evidence_block = "\n".join(evidence)

        system = (
            "You are the Final Response Builder. Return ONLY valid JSON.\n"
            "Use the provided evidence ONLY when it exists. If evidence is empty, answer normally from general reasoning.\n"
            "If you used evidence snippets, mention that you used them (no fake citations).\n\n"
            "Output schema (strict):\n"
            "{\n"
            "  \"reply\": \"string\",\n"
            "  \"confidence\": 0.0-1.0\n"
            "}\n"
        )

        user = (
            f"User request: {user_input}\n\n"
            f"Intent: {json.dumps(intent, ensure_ascii=False)}\n\n"
            f"Tool result (if any): {tool_context or 'NONE'}\n\n"
            f"Evidence snippets (if any):\n{evidence_block or 'NONE'}\n"
        )

        raw = self.client.chat(
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            response_format="json",
            temperature=0.3,
        )

        try:
            data = json.loads(raw)
        except Exception:
            data = {"reply": raw.strip(), "confidence": 0.55}

        state["draft_reply"] = str(data.get("reply", "")).strip()
        state["confidence"] = float(data.get("confidence", 0.7))

        return AgentResult(agent=self.name, status="ok", data=data, confidence=state["confidence"], next=["safety"])
