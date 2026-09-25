from pydantic import BaseModel, Field


class EstimateRequest(BaseModel):
    room_id: int
    tile_id: int
    waste_pct: float | None = Field(
        default=None, description="基础损耗%；缺省取系统默认损耗"
    )
    work_time: float | None = Field(
        default=None, ge=0, lt=24, description="施工钟点，24 小时制小数（22.5=22:30）"
    )
    save: bool = False
    note: str = ""


class EstimateResponse(BaseModel):
    room_id: int
    tile_id: int
    room_name: str
    tile_name: str
    area_m2: float
    piece_m2: float
    raw_count: int
    waste_pct: float
    base_waste_pct: float
    surcharge_pct: float
    order_count: int
    layout: dict
    work_time: float | None = None
    shift_id: int | None = None
    shift_name: str | None = None
    run_id: int | None = None
