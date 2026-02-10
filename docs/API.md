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
```
## 2) Orchestrator – Main AI Pipeline
POST /ask
Processes a user request through the AI Orchestrator pipeline and returns a final structured response.
**Request Body (JSON):**
```json
{
  "message": "Summarize the uploaded documents"
}
```

**Response (200 OK):**
```json
{
  "run_id": "c3b8a4e1-2a9f-4b1e-b5c3-9b9d21a6d101",
  "answer": "Here is a summary of the uploaded documents..."
}
```
**Error Responses:**

400 Bad Request – Missing or invalid input

500 Internal Server Error – Orchestrator failure

### Notes:

The orchestrator may invoke retrieval and tools automatically
Each request is logged as a workflow run

## 3) File Upload & Ingestion
POST /files/upload

Description:
Uploads a single PDF file and ingests it for retrieval-augmented generation.

Request:
multipart/form-data

Form field:

file: PDF file

Example (curl):

curl -X POST http://127.0.0.1:8000/files/upload \
  -F "file=@document.pdf"


Response (200 OK):
```json
{
  "filename": "document.pdf",
  "status": "uploaded"
}
```
POST /files/upload-multiple

Description:
Uploads multiple PDF files in one request.

Request:
multipart/form-data

Form field:

files: list of PDF files

Response (200 OK):
```json
{
  "uploaded": 3,
  "files": ["a.pdf", "b.pdf", "c.pdf"]
}
```

Error Responses:

400 Bad Request – Invalid file type

500 Internal Server Error – Ingestion failure

## 4) Workflow Runs
GET /runs

Description:
Returns a list of workflow runs.

Response (200 OK):
```json
[
  {
    "run_id": "c3b8a4e1-2a9f-4b1e-b5c3-9b9d21a6d101",
    "created_at": "2026-02-10T10:15:00Z"
  }
]
```
GET /runs/{run_id}

Description:
Returns details of a specific workflow run.

Path Parameters:

run_id (string)

Response (200 OK):
```json
{
  "run_id": "c3b8a4e1-2a9f-4b1e-b5c3-9b9d21a6d101",
  "steps": [
    { "agent": "intent", "output": "question" },
    { "agent": "retrieval", "output": "retrieved context" },
    { "agent": "final", "output": "final answer" }
  ]
}
```

Error Responses:

404 Not Found – Run ID not found

## 5) Error Format (General)

All errors follow a standard format:
```json
{
  "detail": "Error message describing what went wrong"
}
```
## 6) Authentication

This API does not currently enforce authentication.
It is intended for local development and educational use.