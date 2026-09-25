from fastapi import HTTPException

from app.engines.shifts import in_window
from app.engines.tile_math import tile_count
from app.repositories import history, rooms, settings_repo, shifts_repo, tiles


def _resolve_shift(work_time: float | None) -> dict | None:
    """Return the first active shift whose window contains work_time, else None."""
    if work_time is None:
        return None
    for shift in shifts_repo.list_shifts(active_only=True):
        if in_window(work_time, shift["start_hour"], shift["end_hour"]):
            return shift
    return None


def run_estimate(
    room_id: int,
    tile_id: int,
    waste_pct: float | None,
    save: bool,
    note: str,
    work_time: float | None = None,
):
    room = rooms.get_room(room_id)
    if not room:
        raise HTTPException(404, "room not found")
    tile = tiles.get_tile(tile_id)
    if not tile:
        raise HTTPException(404, "tile not found")
    if room.get("data_quality") == "dirty":
        raise HTTPException(422, "room marked dirty; fix dimensions before estimate")
    if work_time is not None and not (0 <= float(work_time) < 24):
        raise HTTPException(422, "work_time must be within [0, 24)")

    base_waste = float(waste_pct) if waste_pct is not None else settings_repo.get_waste_pct()
    shift = _resolve_shift(work_time)
    surcharge = float(shift["surcharge_pct"]) if shift else 0.0
    total_waste = base_waste + surcharge

    calc = tile_count(room["length"], room["width"], tile["tile_l"], tile["tile_w"], total_waste)

    run_id = None
    if save:
        run_id = history.insert_run(
            room_id=room_id,
            tile_id=tile_id,
            waste_pct=total_waste,
            result=calc,
            note=note,
            work_time=work_time,
            base_waste_pct=base_waste,
            surcharge_pct=surcharge,
            shift_id=shift["id"] if shift else None,
            shift_name=shift["name"] if shift else None,
        )

    return {
        "room_id": room_id,
        "tile_id": tile_id,
        "room": room,
        "tile": tile,
        "run_id": run_id,
        "work_time": work_time,
        "base_waste_pct": base_waste,
        "surcharge_pct": surcharge,
        "shift_id": shift["id"] if shift else None,
        "shift_name": shift["name"] if shift else None,
        **calc,
    }
