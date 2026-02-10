import os
import pytest

# Ensure this runs BEFORE app imports
os.environ["REQUIRE_MONGO"] = "false"
os.environ.pop("MONGO_URI", None)
os.environ["MAX_AGENT_HOPS"] = "3"
os.environ["OLLAMA_MODEL"] = "test-model"

@pytest.fixture(autouse=True)
def _force_test_mode(monkeypatch):
    from app.core.config import settings
    from app.core import db

    monkeypatch.setattr(settings, "require_mongo", False, raising=False)
    monkeypatch.setattr(settings, "mongo_uri", None, raising=False)

    # Clear cached store between tests
    db._store = None
    yield
    db._store = None
