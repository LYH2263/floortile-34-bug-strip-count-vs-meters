from fastapi import HTTPException

from app.engines.tile_math import tile_count
from app.modules.skirting import EDGES, skirting_usage
from app.repositories import history, rooms, settings_repo, tiles


def run_estimate(
    room_id: int,
    tile_id: int,
    waste_pct: float | None,
    save: bool,
    note: str,
    skirting_edge: str | None = None,
    skirting_strip_len: float | None = None,
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
    calc = tile_count(room["length"], room["width"], tile["tile_l"], tile["tile_w"], waste)

    skirting = None
    if skirting_edge is not None:
        if skirting_edge not in EDGES:
            raise HTTPException(422, "invalid skirting_edge; expected one of: length, width")
        strip_len = (
            float(skirting_strip_len)
            if skirting_strip_len is not None
            else settings_repo.get_skirting_strip_len()
        )
        if strip_len <= 0:
            raise HTTPException(422, "skirting strip length must be > 0")
        skirting = skirting_usage(room["length"], room["width"], skirting_edge, strip_len)
        calc["skirting"] = skirting

    run_id = None
    if save:
        payload = {**calc, "room_id": room_id, "tile_id": tile_id}
        run_id = history.insert_run(room_id, tile_id, waste, payload, note)

    return {
        "room_id": room_id,
        "tile_id": tile_id,
        "room": room,
        "tile": tile,
        "run_id": run_id,
        **calc,
    }
