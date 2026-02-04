from __future__ import annotations

from typing import Any, Dict, List

from app.core.db import get_store
from app.core.config import settings

from app.agents.intent import IntentAgent
from app.agents.retrieval import RetrievalAgent
from app.agents.tool import ToolAgent
from app.agents.safety import SafetyAgent
from app.agents.final_builder import FinalBuilderAgent


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
        store = get_store()

        # Create workflow run (n8n-style execution record)
        run_id = store.create_run(user_id=user_id, input_text=user_message)

        state: Dict[str, Any] = {
            "user_id": user_id,
            "input": user_message,
            "agent_path": [],
            "intent": {},
            "retrieval_hits": [],
            "tool_result": None,
            "draft_reply": "",
            "confidence": 0.5,
            "run_id": run_id,  # optional: allow agents to access it if needed
        }

        queue: List[str] = ["intent"]
        hops = 0

        try:
            while queue and hops < self.max_hops:
                current = queue.pop(0)
                if current not in self.agents:
                    break

                # Run agent
                result = self.agents[current].run(state)

                # Log step output
                store.append_run_step(run_id, current, result)

                # Track agent path
                state["agent_path"].append(current)

                # Next-step routing
                nxt = result.get("next") or []
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
            confidence = max(0.0, min(1.0, confidence))
            agent_path = state.get("agent_path", [])

            # Finalize run
            store.finalize_run(
                run_id=run_id,
                final_reply=reply,
                agent_path=agent_path,
                confidence=confidence,
            )

            return {
                "reply": reply,
                "agent_path": agent_path,
                "confidence": confidence,
                "run_id": run_id,
            }

        except Exception as e:
            # Mark run failed (if you don't have fail_run, we store a "failed" step + finalize as failed-ish)
            try:
                store.append_run_step(run_id, "error", {"error": str(e)})
                # If you later add store.fail_run(), use it here.
                store.finalize_run(
                    run_id=run_id,
                    final_reply="",
                    agent_path=state.get("agent_path", []),
                    confidence=0.0,
                )
            except Exception:
                pass
            raise
