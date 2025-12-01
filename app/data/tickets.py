# tickets.py
from data.db import get_connection

def create_ticket(issue, status="Open", priority="Medium", opened_by=None):
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO it_tickets (issue, status, priority, opened_by) VALUES (?, ?, ?, ?)",
            (issue, status, priority, opened_by)
        )
        return cur.lastrowid

def list_tickets():
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM it_tickets ORDER BY id DESC").fetchall()
    return rows

def get_ticket(ticket_id):
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM it_tickets WHERE id = ?", (ticket_id,)).fetchone()
    return row

def update_ticket(ticket_id, **fields):
    if not fields:
        return False
    cols = ", ".join([f"{k} = ?" for k in fields.keys()])
    vals = list(fields.values()) + [ticket_id]
    sql = f"UPDATE it_tickets SET {cols} WHERE id = ?"
    with get_connection() as conn:
        conn.execute(sql, vals)
    return True

def delete_ticket(ticket_id):
    with get_connection() as conn:
        conn.execute("DELETE FROM it_tickets WHERE id = ?", (ticket_id,))
    return True
