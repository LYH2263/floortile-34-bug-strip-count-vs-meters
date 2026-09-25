from app.config import DEFAULT_SKIRTING_STRIP_LEN, DEFAULT_WASTE_PCT
from app.db import connect


def get_all() -> dict:
    conn = connect()
    try:
        rows = conn.execute("SELECT key, value FROM settings").fetchall()
        out = {r["key"]: r["value"] for r in rows}
        if "waste_pct" not in out:
            out["waste_pct"] = str(DEFAULT_WASTE_PCT)
        if "skirting_strip_len" not in out:
            out["skirting_strip_len"] = str(DEFAULT_SKIRTING_STRIP_LEN)
        return out
    finally:
        conn.close()


def get_waste_pct() -> float:
    raw = get_all().get("waste_pct", str(DEFAULT_WASTE_PCT))
    return float(raw)


def get_skirting_strip_len() -> float:
    raw = get_all().get("skirting_strip_len", str(DEFAULT_SKIRTING_STRIP_LEN))
    return float(raw)


def set_value(key: str, value: str) -> None:
    conn = connect()
    try:
        conn.execute(
            "INSERT INTO settings(key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key, str(value)),
        )
        conn.commit()
    finally:
        conn.close()
