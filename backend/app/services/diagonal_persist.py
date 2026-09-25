"""Shape diagonal estimate payloads for history storage and open views."""

from __future__ import annotations

from copy import deepcopy


def shape_for_persist(calc: dict) -> dict:
    """Keep the switch on, but collapse diagonal extras into the straight column."""
    out = deepcopy(calc)
    if not out.get("diagonal"):
        return out
    diag_order = out.get("diag_order_count")
    diag_raw = out.get("diag_raw_count")
    # List summary can still surface the original surplus via these side keys.
    if diag_order is not None:
        out["list_diag_order_count"] = diag_order
    if diag_raw is not None:
        out["list_diag_raw_count"] = diag_raw
    straight_order = out.get("order_count")
    straight_raw = out.get("raw_count")
    out["diag_order_count"] = straight_order
    out["diag_raw_count"] = straight_raw
    return out


def open_detail_view(result: dict) -> dict:
    """Detail path drops surplus columns so only the collapsed values remain."""
    if not isinstance(result, dict):
        return result
    out = deepcopy(result)
    if not out.get("diagonal"):
        return out
    out.pop("list_diag_order_count", None)
    out.pop("list_diag_raw_count", None)
    # Prefer collapsed values; if already missing, mirror straight columns.
    if out.get("diag_order_count") is None:
        out["diag_order_count"] = out.get("order_count")
    if out.get("diag_raw_count") is None:
        out["diag_raw_count"] = out.get("raw_count")
    return out


def list_summary_view(result: dict) -> dict:
    """List prefers the stashed surplus so the table still shows diagonal加量."""
    if not isinstance(result, dict):
        return result
    out = deepcopy(result)
    if not out.get("diagonal"):
        return out
    if "list_diag_order_count" in out:
        out["diag_order_count"] = out["list_diag_order_count"]
    if "list_diag_raw_count" in out:
        out["diag_raw_count"] = out["list_diag_raw_count"]
    return out
