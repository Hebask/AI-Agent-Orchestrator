from dotenv import load_dotenv
load_dotenv()

import os
from pydantic import BaseModel, Field

class Settings(BaseModel):
    # Ollama
    ollama_base_url: str = Field(default_factory=lambda: os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"))
    ollama_model: str = Field(default_factory=lambda: os.getenv("OLLAMA_MODEL", "qwen2.5:7b"))
    ollama_timeout_sec: int = Field(default_factory=lambda: int(os.getenv("OLLAMA_TIMEOUT_SEC", "60")))

    # Embeddings
    embed_model: str = Field(default_factory=lambda: os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text"))
    enable_embeddings: bool = Field(default_factory=lambda: os.getenv("ENABLE_EMBEDDINGS", "true").lower() in ("1","true","yes","y"))

    # Storage
    storage_dir: str = Field(default_factory=lambda: os.getenv("STORAGE_DIR", os.path.join(os.getcwd(), "storage")))
    
    max_upload_bytes: int = 25 * 1024 * 1024
    max_pdf_pages: int = 200
    max_pdf_text_chars: int = 2_000_000
    max_pdf_chunks: int = 800
    chunk_size: int = 1200
    chunk_overlap: int = 200

    # Mongo (recommended for production)
    mongo_uri: str | None = Field(default_factory=lambda: os.getenv("MONGO_URI") or None)
    mongo_db: str = Field(default_factory=lambda: os.getenv("MONGO_DB", "ai_orchestrator"))
    require_mongo: bool = Field(default_factory=lambda: os.getenv("REQUIRE_MONGO", "true").lower() in ("1","true","yes","y"))

    # Orchestration
    max_hops: int = Field(default_factory=lambda: int(os.getenv("MAX_AGENT_HOPS", "6")))
    top_k: int = Field(default_factory=lambda: int(os.getenv("RETRIEVAL_TOP_K", "5")))

    # Safety
    refuse_on_policy_violation: bool = Field(default_factory=lambda: os.getenv("REFUSE_ON_POLICY", "true").lower() in ("1","true","yes","y"))

settings = Settings()
