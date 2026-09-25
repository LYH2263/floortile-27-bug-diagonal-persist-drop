from app.db import connect


def _run_count() -> int:
    conn = connect()
    try:
        return conn.execute("SELECT COUNT(*) c FROM calc_runs").fetchone()["c"]
    finally:
        conn.close()


def test_estimate_straight_unchanged(client):
    # 同房同砖同损耗：未启用斜铺时与改造前一致（客餐厅 6x4.5 + 600x600 + 8%）
    r = client.get("/api/estimate", params={"room_id": 1, "tile_id": 1}).json()
    assert r["diagonal"] is False
    assert r["raw_count"] == 75
    assert r["order_count"] == 81
    assert r["diag_order_count"] is None
    before = _run_count()
    assert r["run_id"] is None
    assert _run_count() == before  # 试算不落库


def test_estimate_diagonal_with_default_factor(client):
    r = client.get(
        "/api/estimate", params={"room_id": 1, "tile_id": 1, "diagonal": "true"}
    ).json()
    assert r["diagonal"] is True
    assert r["diag_factor"] == 1.1
    assert r["order_count"] == 81  # 正铺仍给出
    assert r["diag_raw_count"] == 83
    assert r["diag_order_count"] == 90


def test_estimate_diagonal_custom_factor(client):
    r = client.get(
        "/api/estimate",
        params={"room_id": 1, "tile_id": 1, "diagonal": "true", "diag_factor": 1.2},
    ).json()
    # ceil(27*1.2/0.36)=90; ceil(90*1.08)=98
    assert r["diag_factor"] == 1.2
    assert r["diag_raw_count"] == 90
    assert r["diag_order_count"] == 98


def test_diag_factor_zero_or_negative_fails_no_row(client):
    for bad in (0, -1.1):
        before = _run_count()
        resp = client.post(
            "/api/estimate",
            json={
                "room_id": 1,
                "tile_id": 1,
                "save": True,
                "diagonal": True,
                "diag_factor": bad,
            },
        )
        assert resp.status_code == 422, bad
        assert _run_count() == before  # 历史行数不变


def test_diag_factor_over_limit_fails_no_row(client):
    before = _run_count()
    resp = client.post(
        "/api/estimate",
        json={
            "room_id": 1,
            "tile_id": 1,
            "save": True,
            "diagonal": True,
            "diag_factor": 2.5,
        },
    )
    assert resp.status_code == 422
    assert _run_count() == before


def test_saved_run_snapshots_diagonal_and_is_not_recomputed(client):
    # 落库：斜铺 1.15 写入该次 run
    saved = client.post(
        "/api/estimate",
        json={
            "room_id": 1,
            "tile_id": 1,
            "save": True,
            "diagonal": True,
            "diag_factor": 1.15,
        },
    ).json()
    # ceil(27*1.15/0.36)=87; ceil(87*1.08)=94
    assert saved["diag_raw_count"] == 87
    assert saved["diag_order_count"] == 94
    run_id = saved["run_id"]

    # 之后只改默认系数
    upd = client.put("/api/settings/diag-factor", json={"diag_factor": 1.5})
    assert upd.status_code == 200
    assert upd.json()["diag_factor"] == 1.5

    # 按 run 编号回看：仍是写入时的斜铺数字
    run = client.get(f"/api/runs/{run_id}").json()
    res = run["result"]
    assert res["diagonal"] is True
    assert res["diag_factor"] == 1.15
    assert res["diag_raw_count"] == 87
    assert res["diag_order_count"] == 94
    assert res["order_count"] == 81


def test_set_diag_factor_rejects_invalid(client):
    assert client.put("/api/settings/diag-factor", json={"diag_factor": 0}).status_code == 422
    assert client.put("/api/settings/diag-factor", json={"diag_factor": -1}).status_code == 422
    assert client.put("/api/settings/diag-factor", json={"diag_factor": 9}).status_code == 422
    # 默认系数未被污染
    assert client.get("/api/settings").json()["diag_factor"] != "0"


def test_saved_run_list_and_detail_show_same_diagonal_columns(client):
    # 落库：斜铺 1.15
    saved = client.post(
        "/api/estimate",
        json={
            "room_id": 1,
            "tile_id": 1,
            "save": True,
            "diagonal": True,
            "diag_factor": 1.15,
        },
    ).json()
    run_id = saved["run_id"]

    detail = client.get(f"/api/runs/{run_id}").json()["result"]
    # 详情：正铺、斜铺分列与落库前回包同一组，加量不得被吞
    assert detail["diagonal"] is True
    assert detail["order_count"] == saved["order_count"] == 81
    assert detail["raw_count"] == saved["raw_count"] == 75
    assert detail["diag_order_count"] == saved["diag_order_count"] == 94
    assert detail["diag_raw_count"] == saved["diag_raw_count"] == 87
    assert detail["diag_factor"] == saved["diag_factor"] == 1.15

    # 列表摘要：与详情同一组斜铺数字
    items = client.get("/api/runs").json()["items"]
    row = next(i for i in items if i["id"] == run_id)["result"]
    assert row["diagonal"] is True
    assert row["order_count"] == 81
    assert row["diag_order_count"] == 94
    assert row["diag_raw_count"] == 87


def test_diagonal_never_below_straight(client):
    # 系数 <1 时斜铺一侧仍不得小于正铺
    r = client.get(
        "/api/estimate",
        params={"room_id": 1, "tile_id": 1, "diagonal": "true", "diag_factor": 0.8},
    ).json()
    assert r["diagonal"] is True
    assert r["diag_raw_count"] >= r["raw_count"]
    assert r["diag_order_count"] >= r["order_count"]
