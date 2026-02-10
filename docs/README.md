# AI Agent Orchestrator – API Documentation

## Overview

This project implements a production-grade AI Agent Orchestrator backend using FastAPI and Ollama.
The system routes user requests through multiple specialized AI agents (intent, retrieval, tool, safety)
before producing a final structured response.

The backend also supports:
- PDF upload and ingestion for Retrieval-Augmented Generation (RAG)
- Workflow run tracking and observability
- Pluggable storage backends (MongoDB or local JSON storage)

This documentation provides:
- API reference
- System architecture
- Configuration guide
- OpenAPI 3.x specification (manual)
- Testing strategy

---

## Core Features

- Multi-step AI orchestration pipeline
- Local LLM inference using Ollama (no paid API)
- File ingestion and semantic search
- Workflow traceability (`/runs`)
- Production-ready FastAPI structure

---

## Base URL

http://127.0.0.1:8000


---

## Main Endpoints

| Method | Endpoint              | Description                        |
|--------|------------------------|------------------------------------|
| GET    | /health               | Health check and config snapshot   |
| POST   | /ask                  | Main AI orchestration endpoint     |
| POST   | /files/upload         | Upload a single PDF                |
| POST   | /files/upload-multiple| Upload multiple PDFs               |
| GET    | /runs                 | List workflow runs                 |
| GET    | /runs/{run_id}        | Get details of a workflow run      |

---

## Documentation Files

- `architecture.md` – Internal system design
- `api.md` – Human-readable API documentation
- `openapi.yaml` – OpenAPI 3.x specification
- `configuration.md` – Environment variables and setup
- `files.md` – File upload & ingestion
- `runs.md` – Workflow run tracking
- `testing.md` – How to run automated tests

---

## How to Run

```bash
uvicorn app.main:app --reload

Then open:
http://127.0.0.1:8000/health

