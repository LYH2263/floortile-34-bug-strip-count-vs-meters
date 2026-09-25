from fastapi import APIRouter, Query

from app.schemas.estimate import EstimateRequest
from app.services import estimate_service

router = APIRouter(tags=["estimates"])


@router.get("/estimate")
def estimate_get(
    room_id: int = Query(...),
    tile_id: int = Query(...),
    waste_pct: float | None = None,
    save: bool = False,
    skirting_edge: str | None = None,
    skirting_strip_len: float | None = None,
):
    return estimate_service.run_estimate(
        room_id, tile_id, waste_pct, save, "", skirting_edge, skirting_strip_len
    )


@router.post("/estimate")
def estimate_post(body: EstimateRequest):
    return estimate_service.run_estimate(
        body.room_id,
        body.tile_id,
        body.waste_pct,
        body.save,
        body.note,
        body.skirting_edge,
        body.skirting_strip_len,
    )
