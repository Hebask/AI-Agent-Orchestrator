from __future__ import annotations

from dotenv import load_dotenv
from fastapi import FastAPI

from app.core.config import settings
from app.api.routes_ask import router as ask_router
from app.api.routes_files import router as files_router
from app.api.routes_runs import router as runs_router

load_dotenv()

app = FastAPI(title="AI Agent Orchestrator (Ollama)")

@app.get("/health")
def health():
    return {
        "status": "ok",
        "ollama_model": settings.ollama_model,
        "storage": "mongo" if settings.mongo_uri else ("local_json" if not settings.require_mongo else "mongo_required_missing_uri"),
        "require_mongo": settings.require_mongo,
        "max_hops": settings.max_hops,
    }

app.include_router(ask_router)   
app.include_router(files_router) 
app.include_router(runs_router) 
