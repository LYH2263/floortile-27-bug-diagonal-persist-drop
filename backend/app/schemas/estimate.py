from pydantic import BaseModel


class EstimateRequest(BaseModel):
    room_id: int
    tile_id: int
    waste_pct: float | None = None
    save: bool = False
    note: str = ""
    diagonal: bool = False
    diag_factor: float | None = None


class EstimateResponse(BaseModel):
    room_id: int
    tile_id: int
    room_name: str
    tile_name: str
    area_m2: float
    piece_m2: float
    raw_count: int
    waste_pct: float
    order_count: int
    layout: dict
    diagonal: bool = False
    diag_factor: float | None = None
    diag_raw_count: int | None = None
    diag_order_count: int | None = None
    run_id: int | None = None


class DiagFactorRequest(BaseModel):
    diag_factor: float
