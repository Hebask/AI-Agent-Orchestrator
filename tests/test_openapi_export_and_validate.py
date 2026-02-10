import json
from pathlib import Path

from openapi_spec_validator import validate_spec


def test_openapi_json_exists_and_valid():
    root = Path(__file__).resolve().parent.parent
    spec_path = root / "openapi.json"

    assert spec_path.exists(), "openapi.json not found. Run: python scripts/export_openapi.py"

    spec = json.loads(spec_path.read_text(encoding="utf-8"))

    validate_spec(spec)
