"""Skirting (收边条) usage: linear meters along one room edge, rounded up to strips."""

from app.engines.helpers import ceil_units

EDGES = ("length", "width")


def skirting_usage(room_l: float, room_w: float, edge: str, strip_len: float) -> dict:
    """
    linear_m: length of the edge where the junction falls (延米)
    strips: ceil(linear_m / strip_len) — 根数
    """
    if edge not in EDGES:
        raise ValueError("invalid skirting edge")
    strip_len = float(strip_len)
    if strip_len <= 0:
        raise ValueError("skirting strip length must be > 0")
    linear_m = round(float(room_l) if edge == "length" else float(room_w), 3)
    return {
        "edge": edge,
        "linear_m": linear_m,
        "strip_len": strip_len,
        "strips": ceil_units(linear_m / strip_len),
    }
