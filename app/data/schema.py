# schema.py
"""
Table creation functions for Week 8 lab (Step 3.1 + 3.2).
All functions accept a sqlite3.Connection object (conn).
"""

def create_users_table(conn):
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user'
        )
    """)
    conn.commit()


def create_cyber_incidents_table(conn):
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cyber_incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            severity TEXT,
            date_reported TEXT,
            reported_by INTEGER,
            FOREIGN KEY (reported_by) REFERENCES users(id)
        )
    """)
    conn.commit()


def create_datasets_metadata_table(conn):
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS datasets_metadata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            rows INTEGER,
            owner INTEGER,
            FOREIGN KEY (owner) REFERENCES users(id)
        )
    """)
    conn.commit()


def create_it_tickets_table(conn):
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS it_tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            issue TEXT NOT NULL,
            status TEXT,
            priority TEXT,
            opened_by INTEGER,
            FOREIGN KEY (opened_by) REFERENCES users(id)
        )
    """)
    conn.commit()


def create_all_tables(conn):
    """
    Master function that creates all tables in the correct order.
    Call this from db.initialize_database() or your setup script.
    """
    create_users_table(conn)
    create_cyber_incidents_table(conn)
    create_datasets_metadata_table(conn)
    create_it_tickets_table(conn)
