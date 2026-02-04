from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict


def tool_now(_: Dict[str, Any]) -> Dict[str, Any]:
    return {"ok": True, "utc": datetime.now(timezone.utc).isoformat()}


def tool_calculator(args: Dict[str, Any]) -> Dict[str, Any]:
    expr = (args.get("expression") or "").strip()
    if not expr:
        return {"ok": False, "error": "Missing 'expression'"}
    # very small safe eval: allow digits, ops, parentheses, dots, spaces
    import re
    if not re.fullmatch(r"[0-9\s\+\-\*\/\(\)\.]+", expr):
        return {"ok": False, "error": "Expression contains invalid characters"}
    try:
        value = eval(expr, {"__builtins__": {}}, {})  # noqa: S307
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": str(e)}
    return {"ok": True, "result": float(value)}

TOOLS = {
    "now": tool_now,
    "calculator": tool_calculator,
}
