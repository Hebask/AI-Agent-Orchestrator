from app.agents.intent import IntentAgent

def test_intent_agent_outputs_fields(monkeypatch):
    # monkeypatch OllamaClient.chat to deterministic output
    from app.core import ollama_client

    def fake_chat(self, messages, **kwargs):
        return '{"intent":"question","needs_retrieval":false,"needs_tools":true,"notes":"math","confidence":0.9}'

    monkeypatch.setattr(ollama_client.OllamaClient, "chat", fake_chat)

    agent = IntentAgent()
    state = {"input": "2+2"}
    res = agent.run(state)

    assert res["status"] == "ok"
    assert "intent" in state
    assert res["next"] == ["tool"]
