import pytest

@pytest.fixture(autouse=True)
def _force_test_env(monkeypatch):
    # Run tests without external services
    monkeypatch.setenv("REQUIRE_MONGO", "false")
    monkeypatch.delenv("MONGO_URI", raising=False)

    # Make orchestration deterministic
    monkeypatch.setenv("MAX_AGENT_HOPS", "3")
    monkeypatch.setenv("OLLAMA_MODEL", "test-model")
