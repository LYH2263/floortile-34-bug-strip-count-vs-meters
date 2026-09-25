import json
from datetime import datetime, timezone

from app.db import connect


def insert_run(
    room_id: int,
    tile_id: int,
    waste_pct: float,
    result: dict,
    note: str = "",
) -> int:
    conn = connect()
    try:
        cur = conn.execute(
            """
            INSERT INTO calc_runs(room_id, tile_id, waste_pct, result_json, note, created_at)
            VALUES (?,?,?,?,?,?)
            """,
            (
                room_id,
                tile_id,
                waste_pct,
                json.dumps(result, ensure_ascii=False),
                note,
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        conn.commit()
        return int(cur.lastrowid)
    finally:
        conn.close()


def list_runs(limit: int = 50, room_id: int | None = None):
    conn = connect()
    try:
        sql = """
            SELECT r.*, rm.name AS room_name, t.name AS tile_name
            FROM calc_runs r
            LEFT JOIN rooms rm ON rm.id = r.room_id
            LEFT JOIN tiles t ON t.id = r.tile_id
        """
        params: list = []
        if room_id is not None:
            sql += " WHERE r.room_id=?"
            params.append(room_id)
        sql += " ORDER BY r.id DESC LIMIT ?"
        params.append(limit)
        rows = conn.execute(sql, params).fetchall()
        out = []
        for row in rows:
            d = dict(row)
            d["result"] = json.loads(d.pop("result_json"))
            out.append(d)
        return out
    finally:
        conn.close()


def get_run(run_id: int):
    conn = connect()
    try:
        row = conn.execute(
            """
            SELECT r.*, rm.name AS room_name, t.name AS tile_name
            FROM calc_runs r
            LEFT JOIN rooms rm ON rm.id = r.room_id
            LEFT JOIN tiles t ON t.id = r.tile_id
            WHERE r.id=?
            """,
            (run_id,),
        ).fetchone()
        if not row:
            return None
        d = dict(row)
        # Return the saved payload verbatim: linear_m, strip_len and strips all
        # belong to the write-time measurement and must not be recounted with
        # the live default strip length.
        d["result"] = json.loads(d.pop("result_json"))
        return d
    finally:
        conn.close()
