import sqlite3


def connect(db_path):
    conn = sqlite3.connect(db_path)
    print(f"Connected to db at #{db_path}")

    conn.row_factory = sqlite3.Row
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS works
        (
            work_id      INTEGER PRIMARY KEY,
            title        TEXT,
            author       TEXT,
            url          TEXT,
            fandoms      TEXT,
            tags         TEXT,
            last_visited TEXT,
            view_count   INTEGER,
            synced_at    TEXT
        )
        """
    )
    return conn
