# datasets.py
from data.db import get_connection

def add_dataset(name, description=None, rows=0, owner=None):
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO datasets_metadata (name, description, rows, owner) VALUES (?, ?, ?, ?)",
            (name, description, rows, owner)
        )
        return cur.lastrowid

def list_datasets():
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM datasets_metadata ORDER BY id DESC").fetchall()
    return rows

def get_dataset(dataset_id):
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM datasets_metadata WHERE id = ?", (dataset_id,)).fetchone()
    return row

def update_dataset(dataset_id, **fields):
    if not fields:
        return False
    cols = ", ".join([f"{k} = ?" for k in fields.keys()])
    vals = list(fields.values()) + [dataset_id]
    sql = f"UPDATE datasets_metadata SET {cols} WHERE id = ?"
    with get_connection() as conn:
        conn.execute(sql, vals)
    return True

def delete_dataset(dataset_id):
    with get_connection() as conn:
        conn.execute("DELETE FROM datasets_metadata WHERE id = ?", (dataset_id,))
    return True
