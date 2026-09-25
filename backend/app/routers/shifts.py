from fastapi import APIRouter, HTTPException

from app.repositories import shifts_repo
from app.schemas.shift import ShiftCreate, ShiftUpdate

router = APIRouter(prefix="/shifts", tags=["shifts"])


@router.get("")
def list_shifts(active_only: bool = False):
    return {"items": shifts_repo.list_shifts(active_only)}


@router.post("", status_code=201)
def create_shift(body: ShiftCreate):
    try:
        return shifts_repo.create_shift(
            body.name, body.start_hour, body.end_hour, body.surcharge_pct, body.active
        )
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.put("/{shift_id}")
def update_shift(shift_id: int, body: ShiftUpdate):
    try:
        row = shifts_repo.update_shift(shift_id, body.model_dump(exclude_unset=True))
    except ValueError as e:
        raise HTTPException(400, str(e))
    if not row:
        raise HTTPException(404, "shift not found")
    return row


@router.delete("/{shift_id}", status_code=204)
def delete_shift(shift_id: int):
    if not shifts_repo.delete_shift(shift_id):
        raise HTTPException(404, "shift not found")
