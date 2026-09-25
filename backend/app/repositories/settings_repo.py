from app.config import DEFAULT_DIAG_FACTOR, DEFAULT_WASTE_PCT, MAX_DIAG_FACTOR
from app.db import connect


def get_all() -> dict:
    conn = connect()
    try:
        rows = conn.execute("SELECT key, value FROM settings").fetchall()
        out = {r["key"]: r["value"] for r in rows}
        if "waste_pct" not in out:
            out["waste_pct"] = str(DEFAULT_WASTE_PCT)
        if "diag_factor" not in out:
            out["diag_factor"] = str(DEFAULT_DIAG_FACTOR)
        return out
    finally:
        conn.close()


def get_waste_pct() -> float:
    raw = get_all().get("waste_pct", str(DEFAULT_WASTE_PCT))
    return float(raw)


def get_diag_factor() -> float:
    raw = get_all().get("diag_factor", str(DEFAULT_DIAG_FACTOR))
    return float(raw)


def set_diag_factor(factor: float) -> float:
    """更新默认斜铺折算系数；0 或超过上限时 ValueError。"""
    factor = float(factor)
    if factor <= 0:
        raise ValueError("斜铺折算系数必须大于 0")
    if factor > MAX_DIAG_FACTOR:
        raise ValueError(f"斜铺折算系数不能超过上限 {MAX_DIAG_FACTOR}")
    conn = connect()
    try:
        conn.execute(
            """
            INSERT INTO settings(key, value) VALUES ('diag_factor', ?)
            ON CONFLICT(key) DO UPDATE SET value=excluded.value
            """,
            (str(factor),),
        )
        conn.commit()
        return factor
    finally:
        conn.close()
