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
    # store user message
    append_message(req.user_id, "user", req.message)

    # run orchestration (includes workflow run logging)
    result = orchestrator.run(req.message, user_id=req.user_id)

    # store assistant message + include run_id in meta
    append_message(
        req.user_id,
        "assistant",
        result.get("reply", ""),
        meta={
            "agent_path": result.get("agent_path", []),
            "confidence": result.get("confidence", 0.0),
            "run_id": result.get("run_id"),
        },
    )

    return result
