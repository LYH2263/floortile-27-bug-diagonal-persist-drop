from fastapi import HTTPException

from app.repositories import history, rooms, settings_repo, tiles
from app.services.estimate_core import build_calc


def run_estimate(
    room_id: int,
    tile_id: int,
    waste_pct: float | None,
    save: bool,
    note: str,
    diagonal: bool = False,
    diag_factor: float | None = None,
):
    room = rooms.get_room(room_id)
    if not room:
        raise HTTPException(404, "room not found")
    tile = tiles.get_tile(tile_id)
    if not tile:
        raise HTTPException(404, "tile not found")
    if room.get("data_quality") == "dirty":
        raise HTTPException(422, "room marked dirty; fix dimensions before estimate")

    waste = float(waste_pct) if waste_pct is not None else settings_repo.get_waste_pct()
    # 斜铺系数为空（启用斜铺）时取默认系数；非法系数在此抛错，先于任何落库
    if diagonal and diag_factor is None:
        diag_factor = settings_repo.get_diag_factor()
    try:
        calc = build_calc(room, tile, waste, diagonal, diag_factor)
    except ValueError as exc:
        raise HTTPException(422, str(exc))

    run_id = None
    if save:
        from app.services.diagonal_persist import shape_for_persist

        # Preview keeps full calc; only the stored snapshot is reshaped.
        payload = {**shape_for_persist(calc), "room_id": room_id, "tile_id": tile_id}
        run_id = history.insert_run(room_id, tile_id, waste, payload, note)

    return {
        "room_id": room_id,
        "tile_id": tile_id,
        "room": room,
        "tile": tile,
        "run_id": run_id,
        **calc,
    }
