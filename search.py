from db import connect, query


def search(args):
    conn = connect(args.db)
    results = query(conn, args)
    for row in results:
        print(f"{row["title"]} [ID: {row["work_id"]}]")
        print(f"  By: {row["author"]}")
        print(f"  Tags: {row["tags"]}")
        print(f"  url: {row["url"]}")
