from pydantic import BaseModel, Field


class ShiftBase(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    start_hour: float = Field(ge=0, lt=24, description="起始钟点，24 小时制小数，如 22.5")
    end_hour: float = Field(ge=0, lt=24, description="结束钟点，可早于起始表示跨午夜")
    surcharge_pct: float = Field(description="在基础损耗上追加的百分点，不可为负")
    active: bool = True


class ShiftCreate(ShiftBase):
    pass


class ShiftUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=50)
    start_hour: float | None = Field(default=None, ge=0, lt=24)
    end_hour: float | None = Field(default=None, ge=0, lt=24)
    surcharge_pct: float | None = None
    active: bool | None = None
