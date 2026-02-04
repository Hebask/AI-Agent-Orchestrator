# Production-Grade AI Agent Orchestrator (Mini n8n Replacement) — Ollama + MongoDB

This project is a **production-style FastAPI backend** that routes a user request through multiple AI agents and returns a **structured JSON response**.

It follows a hop-limited orchestration flow:

**User → Orchestrator → Intent → (Retrieval?) → (Tool?) → Final Builder → Safety → Response**

Example response:
```json
{
  "reply": "You can register online for this service.",
  "agent_path": ["intent", "retrieval", "final", "safety"],
  "confidence": 0.88
}
```

---

## ✅ Project Requirements Coverage

- Python backend: **FastAPI**
- Multi-agent orchestration: **OrchestratorService** controls flow
- Agents return **JSON** (not plain text)
- Orchestrator decides next steps based on agent JSON
- Hop limit to prevent infinite loops (`MAX_AGENT_HOPS`)
- Retrieval from uploaded files and chat history
- Tool execution via **ToolAgent** + tool registry
- Safety validation via **SafetyAgent**
- Production storage: **MongoDB** (required by default)

---

## Endpoints

- `POST /ask`  
  Main agent orchestration endpoint.

- `POST /files/upload?user_id=default`  
  Upload **one** PDF and ingest it.

- `POST /files/upload-multiple?user_id=default`  
  Upload **multiple** PDFs in one request.

- `GET /health`  
  Basic health information.

---

## Folder Structure (Layering)

- `app/api/` — FastAPI routes (HTTP layer only)
- `app/services/` — business logic (orchestration, ingestion, search, chat)
- `app/agents/` — agent implementations (intent/retrieval/tool/final/safety)
- `app/repositories/` — persistence layer (MongoStore + LocalJsonStore fallback)
- `app/core/` — settings, DB wiring, Ollama client
- `app/tools/` — tool registry used by ToolAgent

Routes do not talk directly to Mongo; all DB access goes through repositories/services.

---

## Setup (Zero-Knowledge Friendly)

### 1) Install & Run Ollama
- Install Ollama
- Run:
  ```bash
  ollama serve
  ```
- Pull models:
  ```bash
  ollama pull qwen2.5:7b
  ollama pull nomic-embed-text
  ```

### 2) Install MongoDB
Use local MongoDB or MongoDB Atlas.
Set `.env` with:
```env
MONGO_URI=mongodb://localhost:27017
MONGO_DB=ai_orchestrator
REQUIRE_MONGO=true
```

### 3) Install Python dependencies
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### 4) Run the API
```bash
uvicorn app.main:app --reload
```

---

## How to Upload Multiple PDFs (Postman)

**POST** `http://127.0.0.1:8000/files/upload-multiple?user_id=default`

Body → **form-data**:
- Key: `files` (type **File**) → select PDF
- Add another row with the **same key** `files` → select another PDF

---

## Notes on Storage

- MongoDB stores:
  - `chats`
  - `files`
  - `file_chunks`
- Raw uploaded file bytes are stored under `STORAGE_DIR/files/` so you can re-ingest if needed.

If you want to run without Mongo:
```env
REQUIRE_MONGO=false
```
Then it falls back to local JSON under `storage/` (dev/demo only).

---

## Diagram
See: `app/diagrams/orchestration.mmd`
