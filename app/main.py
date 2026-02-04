from __future__ import annotations

from fastapi import FastAPI

from app.api.routes_ask import router as ask_router
from app.api.routes_files import router as files_router
from app.core.config import settings
from dotenv import load_dotenv
load_dotenv()

app = FastAPI(title="AI Agent Orchestrator")

app.include_router(ask_router, prefix="/ask")
app.include_router(files_router, prefix="/files")

def create_app() -> FastAPI:
    app = FastAPI(title="AI Agent Orchestrator (Ollama)")

    @app.get("/health")
    def health():
        return {
            "status": "ok",
            "ollama_model": settings.ollama_model,
            "storage": "mongo" if settings.mongo_uri else ("local_json" if not settings.require_mongo else "mongo_required_missing_uri"),
            "require_mongo": settings.require_mongo,
        }

    app.include_router(ask_router)
    app.include_router(files_router)
    return app


app = create_app()
