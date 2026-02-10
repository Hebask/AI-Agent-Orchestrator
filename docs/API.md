# AI Agent Orchestrator API (FastAPI + Ollama)

Base URL (local): `http://127.0.0.1:8000`

This backend provides:
- An AI Orchestrator pipeline (`/ask`)
- PDF upload + ingestion (`/files/upload`, `/files/upload-multiple`)
- Workflow run tracking (`/runs`, `/runs/{run_id}`)
- Health/config snapshot (`/health`)

---

## 1) Health

### GET `/health`
Returns service status and key configuration values.

**Example response (200)**
```json
{
  "status": "ok",
  "ollama_model": "qwen3",
  "storage": "mongo|local_json|mongo_required_missing_uri",
  "require_mongo": true,
  "max_hops": 6
}
