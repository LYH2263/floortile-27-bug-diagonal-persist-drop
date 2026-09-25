"""斜铺业务规则：系数校验与测算入参整理（不依赖 FastAPI，便于单测）。"""

from app.config import MAX_DIAG_FACTOR
from app.engines.tile_math import tile_count


def validate_diag_factor(factor: float) -> float:
    """系数必须为正且不超过配置上限，否则 ValueError（接口层映射为 422）。"""
    factor = float(factor)
    if factor <= 0:
        raise ValueError("斜铺折算系数必须大于 0")
    if factor > MAX_DIAG_FACTOR:
        raise ValueError(f"斜铺折算系数不能超过上限 {MAX_DIAG_FACTOR}")
    return factor


def build_calc(
    room: dict,
    tile: dict,
    waste: float,
    diagonal: bool,
    diag_factor: float | None,
) -> dict:
    """组装测算结果；斜铺启用时先校验系数（失败不落库）。"""
    if diagonal:
        diag_factor = validate_diag_factor(diag_factor)
    return tile_count(
        room["length"],
        room["width"],
        tile["tile_l"],
        tile["tile_w"],
        waste,
        diagonal=diagonal,
        diag_factor=diag_factor,
    )
