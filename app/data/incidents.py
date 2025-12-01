# incidents.py
from data.db import get_connection

def create_incident(title, description, severity, date_reported, reported_by=None):
    sql = """
    INSERT INTO cyber_incidents (title, description, severity, date_reported, reported_by)
    VALUES (?, ?, ?, ?, ?)
    """
    with get_connection() as conn:
        cur = conn.execute(sql, (title, description, severity, date_reported, reported_by))
        return cur.lastrowid

def get_all_incidents():
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM cyber_incidents ORDER BY date_reported DESC").fetchall()
    return rows

def get_incident(incident_id):
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM cyber_incidents WHERE id = ?", (incident_id,)).fetchone()
    return row

def search_incidents(keyword):
    q = f"%{keyword}%"
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM cyber_incidents WHERE title LIKE ? OR description LIKE ?",
            (q, q)
        ).fetchall()
    return rows

def update_incident(incident_id, **fields):
    """
    Update arbitrary fields. fields example: severity='High', description='updated'
    """
    if not fields:
        return False
    cols = ", ".join([f"{k} = ?" for k in fields.keys()])
    vals = list(fields.values()) + [incident_id]
    sql = f"UPDATE cyber_incidents SET {cols} WHERE id = ?"
    with get_connection() as conn:
        conn.execute(sql, vals)
    return True

def delete_incident(incident_id):
    with get_connection() as conn:
        conn.execute("DELETE FROM cyber_incidents WHERE id = ?", (incident_id,))
    return True

def count_incidents_by_severity():
    with get_connection() as conn:
        rows = conn.execute("SELECT severity, COUNT(*) AS cnt FROM cyber_incidents GROUP BY severity").fetchall()
    return rows
