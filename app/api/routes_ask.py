from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.orchestrator_service import OrchestratorService
from app.services.chat_service import append_message


router = APIRouter(tags=["chat"])
orchestrator = OrchestratorService()


class AskRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=8000)
    user_id: str = Field(default="default", max_length=128)


@router.post("/ask")
def ask(req: AskRequest):
    append_message(req.user_id, "user", req.message)
    result = orchestrator.run(req.message, user_id=req.user_id)
    append_message(req.user_id, "assistant", result["reply"], meta={"agent_path": result["agent_path"], "confidence": result["confidence"]})
    return result
