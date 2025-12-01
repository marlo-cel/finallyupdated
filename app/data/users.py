# users.py
from data.db import get_connection

def create_user(username, password_hash, role="user"):
    """
    Insert a user record into the users table.
    Returns the new user id.
    """
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (username, password_hash, role)
        )
        return cur.lastrowid

def get_user_by_username(username):
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    return row

def list_users():
    with get_connection() as conn:
        rows = conn.execute("SELECT id, username, role FROM users").fetchall()
    return rows
