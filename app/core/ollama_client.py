from __future__ import annotations

import json
import time
from typing import Any, Dict, List, Optional

import requests


class OllamaError(RuntimeError):
    pass


def _safe_json_loads(s: str) -> Any:
    """Best-effort JSON parse. Raises ValueError if impossible."""
    return json.loads(s)


class OllamaClient:
    def __init__(self, base_url: str, model: str, timeout: int = 60):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    def chat(
        self,
        messages: List[Dict[str, str]],
        *,
        response_format: Optional[str] = "json",
        temperature: float = 0.2,
        max_retries: int = 2,
    ) -> str:
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": temperature},
        }
        if response_format:
            payload["format"] = response_format

        last_err: Exception | None = None
        for attempt in range(max_retries + 1):
            try:
                r = requests.post(
                    f"{self.base_url}/api/chat",
                    json=payload,
                    timeout=self.timeout,
                )
                if r.status_code >= 400:
                    raise OllamaError(f"Ollama /api/chat failed: {r.status_code} {r.text[:500]}")
                data = r.json()
                return (data.get("message", {}) or {}).get("content", "") or ""
            except Exception as e:  # noqa: BLE001
                last_err = e
                if attempt < max_retries:
                    time.sleep(0.3 * (attempt + 1))
                    continue
                raise

        raise last_err or OllamaError("Unknown Ollama error")

    def embeddings(self, text: str, *, model: Optional[str] = None) -> List[float]:
        payload = {"model": model or self.model, "prompt": text}
        r = requests.post(f"{self.base_url}/api/embeddings", json=payload, timeout=self.timeout)
        if r.status_code >= 400:
            raise OllamaError(f"Ollama /api/embeddings failed: {r.status_code} {r.text[:500]}")
        data = r.json()
        emb = data.get("embedding")
        if not isinstance(emb, list):
            raise OllamaError("Ollama embeddings response missing 'embedding'")
        return [float(x) for x in emb]
