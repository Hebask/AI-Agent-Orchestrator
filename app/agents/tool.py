from __future__ import annotations

import json
from typing import Any, Dict

from app.agents.base import BaseAgent, AgentResult
from app.core.config import settings
from app.core.ollama_client import OllamaClient
from app.tools.registry import TOOLS


class ToolAgent(BaseAgent):
    name = "tool"

    def __init__(self) -> None:
        self.client = OllamaClient(settings.ollama_base_url, settings.ollama_model, timeout=settings.ollama_timeout_sec)

    def run(self, state: Dict[str, Any]) -> AgentResult:
        user_input = state.get("input", "") or ""

        system = (
            "You are a Tool Selection Agent. Return ONLY valid JSON.\n"
            "Available tools: calculator, now.\n"
            "Choose tool_name and tool_args.\n"
            "Schema: {\"tool_name\":\"calculator|now|none\",\"tool_args\":{...},\"confidence\":0.0-1.0}\n"
            "Examples:\n"
            "- For '25500 + 47500' => tool_name=calculator, tool_args={expression:'25500+47500'}\n"
            "- For 'what time is it' => tool_name=now\n"
        )

        raw = self.client.chat(
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user_input}],
            response_format="json",
        )

        try:
            pick = json.loads(raw)
        except Exception:
            pick = {"tool_name": "none", "tool_args": {}, "confidence": 0.3}

        tool_name = (pick.get("tool_name") or "none").strip()
        tool_args = pick.get("tool_args") if isinstance(pick.get("tool_args"), dict) else {}

        if tool_name in TOOLS:
            result = TOOLS[tool_name](tool_args)
            state["tool_result"] = {"tool": tool_name, "args": tool_args, "result": result}
            return AgentResult(agent=self.name, status="ok", data=state["tool_result"], confidence=float(pick.get("confidence", 0.7)), next=["final"])

        state["tool_result"] = None
        return AgentResult(agent=self.name, status="ok", data={"tool": "none"}, confidence=float(pick.get("confidence", 0.5)), next=["final"])
