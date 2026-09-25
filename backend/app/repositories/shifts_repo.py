from app.db import connect
from app.engines.shifts import validate_window


def _to_dict(row) -> dict:
    d = dict(row)
    d["active"] = bool(d["active"])
    return d


def list_shifts(active_only: bool = False) -> list[dict]:
    conn = connect()
    try:
        sql = "SELECT * FROM shifts"
        if active_only:
            sql += " WHERE active = 1"
        sql += " ORDER BY id"
        return [_to_dict(r) for r in conn.execute(sql).fetchall()]
    finally:
        conn.close()


def get_shift(shift_id: int) -> dict | None:
    conn = connect()
    try:
        row = conn.execute("SELECT * FROM shifts WHERE id=?", (shift_id,)).fetchone()
        return _to_dict(row) if row else None
    finally:
        conn.close()


def _validate(name, start_hour, end_hour, surcharge_pct):
    err = validate_window(start_hour, end_hour)
    if err:
        raise ValueError(err)
    if surcharge_pct is not None and surcharge_pct < 0:
        raise ValueError("surcharge_pct must not be negative")
    if not name or not str(name).strip():
        raise ValueError("name must not be empty")


def create_shift(name, start_hour, end_hour, surcharge_pct, active=True) -> dict:
    _validate(name, start_hour, end_hour, surcharge_pct)
    conn = connect()
    try:
        cur = conn.execute(
            "INSERT INTO shifts(name,start_hour,end_hour,surcharge_pct,active) VALUES (?,?,?,?,?)",
            (name.strip(), float(start_hour), float(end_hour), float(surcharge_pct), 1 if active else 0),
        )
        conn.commit()
        return get_shift(int(cur.lastrowid))
    finally:
        conn.close()


def update_shift(shift_id: int, changes: dict) -> dict | None:
    current = get_shift(shift_id)
    if not current:
        return None
    merged = {**current, **{k: v for k, v in changes.items() if v is not None}}
    _validate(merged["name"], merged["start_hour"], merged["end_hour"], merged["surcharge_pct"])
    conn = connect()
    try:
        conn.execute(
            "UPDATE shifts SET name=?,start_hour=?,end_hour=?,surcharge_pct=?,active=? WHERE id=?",
            (
                merged["name"].strip(),
                float(merged["start_hour"]),
                float(merged["end_hour"]),
                float(merged["surcharge_pct"]),
                1 if merged["active"] else 0,
                shift_id,
            ),
        )
        conn.commit()
    finally:
        conn.close()
    return get_shift(shift_id)


def delete_shift(shift_id: int) -> bool:
    conn = connect()
    try:
        cur = conn.execute("DELETE FROM shifts WHERE id=?", (shift_id,))
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()
