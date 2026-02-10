# AI Agent Orchestrator API (FastAPI + Ollama)

Base URL (local): `http://127.0.0.1:8000`

This backend provides:
- An AI Orchestrator pipeline (`POST /ask`)
- PDF upload + ingestion (`POST /files/upload`, `POST /files/upload-multiple`)
- Workflow run tracking (`GET /runs`, `GET /runs/{run_id}`)
- Health/config snapshot (`GET /health`)

---

## 1) Health

### GET `/health`
Returns service status and key configuration values.

**Example response (200)**
```json
{
  "status": "ok",
  "ollama_model": "qwen3",
  "storage": "mongo",
  "require_mongo": true,
  "max_hops": 6
}
