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


def test_diagonal_never_below_straight_when_factor_under_one():
    # 系数 <1：斜铺净用量/订货片数以正铺为下限
    r = tile_count(6.0, 4.5, 0.6, 0.6, 8.0, diagonal=True, diag_factor=0.8)
    assert r["diag_raw_count"] == r["raw_count"] == 75
    assert r["diag_order_count"] == r["order_count"] == 81


def test_shape_for_persist_keeps_snapshot_verbatim():
    from app.services.diagonal_persist import shape_for_persist

    calc = tile_count(6.0, 4.5, 0.6, 0.6, 8.0, diagonal=True, diag_factor=1.15)
    shaped = shape_for_persist(calc)
    # 落库快照与测算回包同一组：斜铺加量不得折叠进正铺列
    assert shaped == calc
    assert shaped["diag_raw_count"] == 87
    assert shaped["diag_order_count"] == 94
    assert shaped["order_count"] == 81
    assert "list_diag_order_count" not in shaped
    assert "list_diag_raw_count" not in shaped


def test_read_views_restore_legacy_collapsed_rows():
    from app.services.diagonal_persist import list_summary_view, open_detail_view

    # 旧 bug 写坏的行：斜铺列被压成正铺值，真值藏在 list_diag_* 侧键
    legacy = {
        "diagonal": True,
        "diag_factor": 1.15,
        "raw_count": 75,
        "order_count": 81,
        "diag_raw_count": 75,
        "diag_order_count": 81,
        "list_diag_raw_count": 87,
        "list_diag_order_count": 94,
    }
    for view in (open_detail_view, list_summary_view):
        out = view(legacy)
        assert out["diag_raw_count"] == 87
        assert out["diag_order_count"] == 94
        assert out["order_count"] == 81
        assert "list_diag_raw_count" not in out
        assert "list_diag_order_count" not in out
    # 两个视图读同一组数
    assert open_detail_view(legacy)["diag_order_count"] == list_summary_view(legacy)[
        "diag_order_count"
    ]
