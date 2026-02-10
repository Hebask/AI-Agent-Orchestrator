import os
import shutil
import tempfile
import pytest
from fastapi.testclient import TestClient

# Ensure this runs BEFORE app imports
os.environ["REQUIRE_MONGO"] = "false"
os.environ.pop("MONGO_URI", None)
os.environ["MAX_AGENT_HOPS"] = "3"
os.environ["OLLAMA_MODEL"] = "test-model"


@pytest.fixture(scope="session", autouse=True)
def _session_test_storage():
    """
    Create a clean temp storage directory so tests do not depend on any existing storage/*.json.
    """
    tmp_dir = tempfile.mkdtemp(prefix="aio_test_storage_")
    os.environ["STORAGE_DIR"] = tmp_dir
    yield tmp_dir
    shutil.rmtree(tmp_dir, ignore_errors=True)


@pytest.fixture(autouse=True)
def _force_test_mode(monkeypatch):
    """
    Force test mode:
    - Disable MongoDB
    - Use temp STORAGE_DIR
    - Reset cached store between tests
    - Mock Ollama client
    """
    from app.core.config import settings
    from app.core import db
    from app.core.ollama_client import OllamaClient

    monkeypatch.setattr(settings, "require_mongo", False, raising=False)
    monkeypatch.setattr(settings, "mongo_uri", None, raising=False)
    monkeypatch.setattr(settings, "storage_dir", os.environ["STORAGE_DIR"], raising=False)

    # ---- Mock Ollama so tests do not require a running model ----
    def _fake_chat(self, messages, *, response_format="json", temperature=0.2, max_retries=2):
        system = ""
        for m in messages:
            if m.get("role") == "system":
                system = m.get("content", "")
                break

        # Intent Agent
        if "Intent Classification Agent" in system:
            return (
                '{"intent":"question","use_retrieval":false,"use_tools":false,'
                '"notes":"test stub","confidence":0.99}'
            )

        # Retrieval Agent (if ever called)
        if "Retrieval Agent" in system or "retrieval" in system.lower():
            return '{"query":"Hello","top_k":3,"notes":"test stub","confidence":0.9}'

        # Safety Agent
        if "Safety" in system:
            return '{"ok":true,"reason":"test stub"}'

        # Final Agent (fallback)
        return '{"reply":"Hello! (mocked)","confidence":0.9}'

    monkeypatch.setattr(OllamaClient, "chat", _fake_chat, raising=True)

    # Reset store between tests
    db._store = None
    yield
    db._store = None


@pytest.fixture(scope="session")
def client():
    """
    Shared FastAPI test client for all tests.
    """
    from app.main import app
    with TestClient(app) as c:
        yield c
