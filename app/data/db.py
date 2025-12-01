# db.py
import sqlite3
from pathlib import Path

DB_DIR = Path(__file__).resolve().parent / "db"
DB_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DB_DIR / "incidents.db"

def get_connection():
    """
    Returns a sqlite3.Connection with foreign keys enabled and row_factory -> sqlite3.Row.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    # enable foreign key enforcement in SQLite
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def initialize_database():
    """
    Create the database file (if not exists) and create all tables by calling schema.create_all_tables.
    This import is done here to avoid circular import problems.
    """
    # import here to avoid top-level circular imports
    from data.schema import create_all_tables

    # Ensure db dir exists (already done) then initialize
    conn = get_connection()
    try:
        create_all_tables(conn)
    finally:
        conn.close()
