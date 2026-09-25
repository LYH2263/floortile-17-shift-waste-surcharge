from fastapi import APIRouter, Query

from app.schemas.estimate import EstimateRequest
from app.services import estimate_service

router = APIRouter(tags=["estimates"])


@router.get("/estimate")
def estimate_get(
    room_id: int = Query(...),
    tile_id: int = Query(...),
    waste_pct: float | None = None,
    work_time: float | None = Query(default=None, ge=0, lt=24),
    save: bool = False,
):
    return estimate_service.run_estimate(
        room_id, tile_id, waste_pct, save, "", work_time
    )


@router.post("/estimate")
def estimate_post(body: EstimateRequest):
    return estimate_service.run_estimate(
        body.room_id,
        body.tile_id,
        body.waste_pct,
        body.save,
        body.note,
        body.work_time,
    )
