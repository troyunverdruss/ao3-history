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
            synced_at    TIMESTAMP
        )
        """
    )
    return conn

def upsert(conn, work):
    conn.execute(
        """
        INSERT INTO works (work_id, title, author, url, fandoms, tags, synced_at)
        VALUES (:work_id, :title, :author, :url, :fandoms, :tags, CURRENT_TIMESTAMP)
        ON CONFLICT(work_id) DO UPDATE SET title=excluded.title,
                                           author=excluded.author,
                                           url=excluded.url,
                                           fandoms=excluded.fandoms,
                                           tags=excluded.tags,
                                           synced_at=excluded.synced_at
        """,
        work,
    )
    conn.commit()
