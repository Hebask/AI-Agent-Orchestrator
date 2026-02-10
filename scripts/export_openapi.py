import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.main import app 


def main() -> None:
    out_path = ROOT / "openapi.json"
    schema = app.openapi()
    out_path.write_text(json.dumps(schema, indent=2), encoding="utf-8")
    print(f"✅ OpenAPI exported to: {out_path}")


if __name__ == "__main__":
    main()
