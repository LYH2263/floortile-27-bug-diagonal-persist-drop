"""斜铺（45° 对角铺贴）订货片数。

斜铺按面积法：用斜向折算系数把房间面积放大，向上取整得到斜铺净用量，
再套与正铺相同的损耗率得到斜铺订货片数。
"""

from app.engines.helpers import ceil_units


def diagonal_count(
    room_l: float,
    room_w: float,
    tile_l: float,
    tile_w: float,
    waste_pct: float,
    factor: float,
) -> dict:
    """
    diag_raw_count:   ceil(room_area * factor / tile_piece_area)
    diag_order_count: ceil(diag_raw * (1 + waste_pct/100))
    """
    area = float(room_l) * float(room_w)
    piece = float(tile_l) * float(tile_w)
    if piece <= 0 or area < 0:
        raise ValueError("invalid dimensions")
    factor = float(factor)
    if factor <= 0:
        raise ValueError("diagonal factor must be positive")
    diag_raw = ceil_units(area * factor / piece)
    diag_order = ceil_units(diag_raw * (1 + float(waste_pct) / 100.0))
    return {
        "diag_factor": factor,
        "diag_raw_count": diag_raw,
        "diag_order_count": diag_order,
    }
