from fastapi import APIRouter, HTTPException
from app.core.db import get_store

router = APIRouter(prefix="/runs", tags=["runs"])


@router.get("/{run_id}")
def get_run(run_id: str):
    store = get_store()
    run = store.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


@router.get("/")
def list_runs(user_id: str = "default", limit: int = 20):
    store = get_store()
    return {"items": store.list_runs(user_id=user_id, limit=limit)}
