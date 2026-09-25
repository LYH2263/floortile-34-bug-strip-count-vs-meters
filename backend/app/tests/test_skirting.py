import json
import sqlite3

import pytest
from fastapi import HTTPException

from app.modules.skirting import skirting_usage
from app.repositories import history as history_repo
from app.services import estimate_service


def test_skirting_length_edge():
    s = skirting_usage(6.0, 4.5, "length", 2.5)
    assert s["edge"] == "length"
    assert s["linear_m"] == 6.0
    assert s["strip_len"] == 2.5
    assert s["strips"] == 3


def test_skirting_width_edge():
    s = skirting_usage(6.0, 4.5, "width", 2.5)
    assert s["linear_m"] == 4.5
    assert s["strips"] == 2


def test_skirting_exact_division():
    s = skirting_usage(6.0, 4.5, "length", 2.0)
    assert s["strips"] == 3


def test_skirting_strip_len_not_positive():
    with pytest.raises(ValueError):
        skirting_usage(6.0, 4.5, "length", 0)
    with pytest.raises(ValueError):
        skirting_usage(6.0, 4.5, "length", -1.0)


def test_skirting_invalid_edge():
    with pytest.raises(ValueError):
        skirting_usage(6.0, 4.5, "diagonal", 2.5)


ROOM = {"id": 1, "name": "客餐厅", "length": 6.0, "width": 4.5, "data_quality": "clean", "note": ""}
TILE = {"id": 1, "name": "600x600", "tile_l": 0.6, "tile_w": 0.6, "data_quality": "clean"}


@pytest.fixture
def fake_repos(monkeypatch):
    saved = []
    monkeypatch.setattr(estimate_service.rooms, "get_room", lambda rid: dict(ROOM))
    monkeypatch.setattr(estimate_service.tiles, "get_tile", lambda tid: dict(TILE))
    monkeypatch.setattr(estimate_service.settings_repo, "get_waste_pct", lambda: 8.0)
    monkeypatch.setattr(estimate_service.settings_repo, "get_skirting_strip_len", lambda: 2.5)
    monkeypatch.setattr(
        estimate_service.history,
        "insert_run",
        lambda room_id, tile_id, waste, payload, note: saved.append(payload) or 1,
    )
    return saved


def test_no_edge_no_skirting_fields(fake_repos):
    r = estimate_service.run_estimate(1, 1, None, False, "")
    assert "skirting" not in r
    assert r["order_count"] == 81


def test_skirting_listed_separately_from_floor(fake_repos):
    r = estimate_service.run_estimate(1, 1, None, False, "", "length", None)
    assert r["order_count"] == 81
    assert r["skirting"]["linear_m"] == 6.0
    assert r["skirting"]["strips"] == 3
    assert r["skirting"]["strip_len"] == 2.5


def test_skirting_strip_len_override(fake_repos):
    r = estimate_service.run_estimate(1, 1, None, False, "", "width", 1.0)
    assert r["skirting"]["linear_m"] == 4.5
    assert r["skirting"]["strip_len"] == 1.0
    assert r["skirting"]["strips"] == 5


def test_invalid_edge_422(fake_repos):
    with pytest.raises(HTTPException) as ei:
        estimate_service.run_estimate(1, 1, None, False, "", "diagonal", None)
    assert ei.value.status_code == 422


def test_strip_len_not_positive_422(fake_repos):
    for bad in (0, -1.0):
        with pytest.raises(HTTPException) as ei:
            estimate_service.run_estimate(1, 1, None, False, "", "length", bad)
        assert ei.value.status_code == 422


def test_saved_payload_keeps_write_time_strip_len(fake_repos, monkeypatch):
    estimate_service.run_estimate(1, 1, None, True, "", "width", None)
    first = fake_repos[0]
    assert first["skirting"]["strip_len"] == 2.5
    assert first["skirting"]["strips"] == 2

    # system default changes later: old payload must keep its write-time numbers
    monkeypatch.setattr(estimate_service.settings_repo, "get_skirting_strip_len", lambda: 5.0)
    estimate_service.run_estimate(1, 1, None, True, "", "width", None)
    second = fake_repos[1]
    assert second["skirting"]["strip_len"] == 5.0
    assert second["skirting"]["strips"] == 1
    assert first["skirting"]["strip_len"] == 2.5
    assert first["skirting"]["strips"] == 2


@pytest.fixture
def isolated_db(tmp_path, monkeypatch):
    from app import db as db_mod
    from app.seed import init_db

    db_file = tmp_path / "test.db"
    monkeypatch.setattr(db_mod, "DB_PATH", db_file)
    init_db()
    return db_file


def test_get_run_keeps_write_time_skirting_set(isolated_db):
    # written with the 2.5 m default: 4.5 延米 -> 2 strips
    saved = {
        "order_count": 81,
        "skirting": {"edge": "width", "linear_m": 4.5, "strip_len": 2.5, "strips": 2},
    }
    conn = sqlite3.connect(isolated_db)
    cur = conn.execute(
        "INSERT INTO calc_runs(room_id, tile_id, waste_pct, result_json, note, created_at)"
        " VALUES (1,1,8,?,'','2026-09-25T00:00:00+00:00')",
        (json.dumps(saved, ensure_ascii=False),),
    )
    run_id = int(cur.lastrowid)
    conn.commit()
    conn.close()

    from app.repositories import settings_repo

    # live default changes to another legal value before the run is reopened
    settings_repo.set_value("skirting_strip_len", "1.3")  # would recount to 4 strips

    row = history_repo.get_run(run_id)
    sk = row["result"]["skirting"]
    assert sk["linear_m"] == 4.5
    assert sk["strip_len"] == 2.5
    assert sk["strips"] == 2
