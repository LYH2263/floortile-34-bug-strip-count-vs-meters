from fastapi import APIRouter, HTTPException

from app.repositories import history as history_repo

router = APIRouter(tags=["history"])


@router.get("/runs")
def list_runs(limit: int = 50, room_id: int | None = None):
    return {"items": history_repo.list_runs(limit, room_id)}


@router.get("/runs/{run_id}")
def get_run(run_id: int):
    row = history_repo.get_run(run_id)
    if not row:
        raise HTTPException(404, "run not found")
    return row
