#!/usr/bin/env python3

import argparse
import os
import sys

import requests

from fetch import sync
from search import search

DEFAULT_BASE_URL = "http://localhost:3001"
DEFAULT_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "history.db")

def main():
    p = argparse.ArgumentParser(description="Download and search your AO3 reading history.")
    p.add_argument("--base-url", default=DEFAULT_BASE_URL, help=f"AO3 base URL (default: {DEFAULT_BASE_URL})")
    p.add_argument("--db", default=DEFAULT_DB, help=f"SQLite DB path (default: {DEFAULT_DB})")
    sub = p.add_subparsers(dest="command", required=True)

    sp = sub.add_parser("sync", help="Download your history into the local DB.")
    sp.add_argument("--username", required=True)
    sp.add_argument("--password", help="Password (else $AO3_PASSWORD or prompt).")
    sp.add_argument("--delay", type=float, default=1.0, help="Minimum seconds between requests")
    sp.set_defaults(func=sync)

    sp = sub.add_parser("search", help="Search stored history by title/tags.")
    sp.add_argument("query", nargs="?", default="", help="Free text (matches title, tags, fandoms, author).")
    sp.add_argument("--tag", help="Require this tag.")
    sp.add_argument("--limit", type=int, default=25)
    sp.set_defaults(func=search)

    args = p.parse_args()
    try:
        args.func(args)
    except (RuntimeError, requests.RequestException) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
