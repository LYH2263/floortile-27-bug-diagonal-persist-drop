"""Floor tile order count: area method + optional grid layout preview."""

from app.engines.helpers import ceil_units
from app.modules.diagonal_layout import diagonal_count


def tile_count(
    room_l: float,
    room_w: float,
    tile_l: float,
    tile_w: float,
    waste_pct: float,
    diagonal: bool = False,
    diag_factor: float | None = None,
) -> dict:
    """
    raw_count: ceil(room_area / tile_piece_area)
    order_count: ceil(raw * (1 + waste_pct/100))

    diagonal=True 时额外返回斜铺净用量/订货片数与折算系数；
    未启用时结果与正铺完全一致。
    """
    area = float(room_l) * float(room_w)
    piece = float(tile_l) * float(tile_w)
    if piece <= 0 or area < 0:
        raise ValueError("invalid dimensions")
    raw = ceil_units(area / piece)
    with_waste = ceil_units(raw * (1 + float(waste_pct) / 100.0))
    layout = layout_preview(room_l, room_w, tile_l, tile_w)
    result = {
        "area_m2": round(area, 3),
        "piece_m2": round(piece, 4),
        "raw_count": raw,
        "waste_pct": float(waste_pct),
        "order_count": with_waste,
        "layout": layout,
        "diagonal": bool(diagonal),
        "diag_factor": None,
        "diag_raw_count": None,
        "diag_order_count": None,
    }
    if diagonal:
        if diag_factor is None:
            raise ValueError("diag_factor required when diagonal enabled")
        result.update(
            diagonal_count(room_l, room_w, tile_l, tile_w, waste_pct, diag_factor)
        )
    return result


def layout_preview(room_l: float, room_w: float, tile_l: float, tile_w: float) -> dict:
    """Grid count if tiles are laid on a full rectangular lattice (may exceed area method)."""
    cols = ceil_units(float(room_l) / float(tile_l))
    rows = ceil_units(float(room_w) / float(tile_w))
    grid_count = cols * rows
    return {
        "cols": cols,
        "rows": rows,
        "grid_count": grid_count,
    }
