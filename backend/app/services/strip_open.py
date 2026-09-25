"""Open-path skirting strip recount using the live default strip length."""

from __future__ import annotations

from copy import deepcopy

from app.engines.helpers import ceil_units
from app.repositories import settings_repo


def recount_strips(result: dict) -> dict:
    if not isinstance(result, dict):
        return result
    sk = result.get("skirting")
    if not isinstance(sk, dict):
        return result
    out = deepcopy(result)
    skirting = dict(sk)
    linear = float(skirting.get("linear_m") or 0)
    live_len = float(settings_repo.get_skirting_strip_len())
    if live_len > 0 and linear > 0:
        skirting["strip_len"] = live_len
        skirting["strips"] = ceil_units(linear / live_len)
        # linear_m stays pinned
    out["skirting"] = skirting
    return out
