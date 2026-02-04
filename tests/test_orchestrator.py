from app.services.orchestrator_service import OrchestratorService

def test_orchestrator_basic_flow(monkeypatch):
    # Patch all agents to avoid calling Ollama
    from app.agents import intent as intent_mod
    from app.agents import tool as tool_mod
    from app.agents import final_builder as final_mod
    from app.agents import safety as safety_mod

    def intent_run(self, state):
        state["intent"] = {"needs_tools": True, "needs_retrieval": False, "confidence": 0.9}
        return {"agent": "intent", "status": "ok", "data": state["intent"], "confidence": 0.9, "next": ["tool"]}

    def tool_run(self, state):
        state["tool_result"] = {"tool": "calculator", "result": {"ok": True, "result": 4.0}}
        return {"agent": "tool", "status": "ok", "data": state["tool_result"], "confidence": 0.9, "next": ["final"]}

    def final_run(self, state):
        state["draft_reply"] = "4"
        state["confidence"] = 0.9
        return {"agent": "final", "status": "ok", "data": {"reply":"4","confidence":0.9}, "confidence": 0.9, "next": ["safety"]}

    def safety_run(self, state):
        return {"agent": "safety", "status": "ok", "data": {"blocked": False}, "confidence": 1.0, "next": ["stop"]}

    monkeypatch.setattr(intent_mod.IntentAgent, "run", intent_run)
    monkeypatch.setattr(tool_mod.ToolAgent, "run", tool_run)
    monkeypatch.setattr(final_mod.FinalBuilderAgent, "run", final_run)
    monkeypatch.setattr(safety_mod.SafetyAgent, "run", safety_run)

    orch = OrchestratorService(max_hops=6)
    out = orch.run("2+2", user_id="u1")

    assert out["reply"] == "4"
    assert "intent" in out["agent_path"]
    assert out["confidence"] >= 0.0
