import pytest

from app import db, seed
from app.engines.tile_math import tile_count
from app.modules.diagonal_layout import diagonal_count


def test_diagonal_guest_room_factor_1_1():
    # 6.0x4.5 房间，0.6x0.6 砖，损耗 8%，系数 1.1
    r = tile_count(6.0, 4.5, 0.6, 0.6, 8.0, diagonal=True, diag_factor=1.1)
    # 正铺：raw 75, order 81
    assert r["raw_count"] == 75
    assert r["order_count"] == 81
    # 斜铺：ceil(27*1.1/0.36)=83；ceil(83*1.08)=90
    assert r["diagonal"] is True
    assert r["diag_factor"] == 1.1
    assert r["diag_raw_count"] == 83
    assert r["diag_order_count"] == 90


def test_diagonal_factor_one_equals_straight():
    r = tile_count(6.0, 4.5, 0.6, 0.6, 8.0, diagonal=True, diag_factor=1.0)
    assert r["diag_raw_count"] == r["raw_count"] == 75
    assert r["diag_order_count"] == r["order_count"] == 81


def test_disabled_diagonal_matches_straight():
    # 未启用：斜铺字段为空，正铺与改造前一致
    r = tile_count(8.0, 1.2, 0.8, 0.8, 8.0)
    assert r["diagonal"] is False
    assert r["diag_order_count"] is None
    assert r["diag_raw_count"] is None
    assert r["raw_count"] == 15
    assert r["order_count"] == 17


def test_diagonal_module_rejects_nonpositive():
    with pytest.raises(ValueError):
        diagonal_count(6.0, 4.5, 0.6, 0.6, 8.0, 0.0)
    with pytest.raises(ValueError):
        diagonal_count(6.0, 4.5, 0.6, 0.6, 8.0, -0.2)
