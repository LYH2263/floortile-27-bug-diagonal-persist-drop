"""Shape diagonal estimate payloads for history storage and open views."""

from __future__ import annotations

from copy import deepcopy


def shape_for_persist(calc: dict) -> dict:
    """落库快照必须与测算回包同为一组：正铺、斜铺分列原样保留，
    不得把斜铺加量折叠进正铺列。"""
    return deepcopy(calc)


def _restore_legacy_stash(out: dict) -> dict:
    """兼容曾被折叠写坏的旧行：真值当时被塞进 list_diag_* 侧键，
    读取时折回斜铺列，使列表与详情看到同一组数字。"""
    if not out.get("diagonal"):
        return out
    if out.get("list_diag_order_count") is not None:
        out["diag_order_count"] = out["list_diag_order_count"]
    if out.get("list_diag_raw_count") is not None:
        out["diag_raw_count"] = out["list_diag_raw_count"]
    out.pop("list_diag_order_count", None)
    out.pop("list_diag_raw_count", None)
    return out


def open_detail_view(result: dict) -> dict:
    """详情视图：快照原样返回（仅对旧坏行做兼容还原）。"""
    if not isinstance(result, dict):
        return result
    return _restore_legacy_stash(deepcopy(result))


def list_summary_view(result: dict) -> dict:
    """列表摘要：与详情读同一组数，不再另取侧键。"""
    if not isinstance(result, dict):
        return result
    return _restore_legacy_stash(deepcopy(result))
