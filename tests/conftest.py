import os
import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

@pytest.fixture(autouse=True)
def _test_env_defaults(monkeypatch):
    """
    Ensure tests run without requiring external services (Mongo/Ollama).
    """
    monkeypatch.setenv("REQUIRE_MONGO", "false")

    monkeypatch.delenv("MONGO_URI", raising=False)

    monkeypatch.setenv("MAX_HOPS", "3")
    monkeypatch.setenv("OLLAMA_MODEL", "test-model")