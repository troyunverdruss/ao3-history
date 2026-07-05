import sqlite3


def connect(db_path):
    conn = sqlite3.connect(db_path)

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

def query(conn, args):
    query = args.query
    tags = args.tag
    sql = """
        SELECT * FROM works
    """
    params = []
    if query is not None or tags is not None:
        sql += " WHERE "
    if query is not None:
        sql += "(title LIKE ? OR author LIKE ?)"
        params.append(f"%{query}%")
        params.append(f"%{query}%")
    if tags is not None:

        for tag in tags:
            sql += " AND tags LIKE ?"
            params.append(f"%{tag}%")

    return conn.execute(sql, params).fetchall()
