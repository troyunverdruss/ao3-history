import getpass
import os
import time

from bs4 import BeautifulSoup

from db import connect, upsert
from requests import Session

MIN_MILLIS_BETWEEN_REQUESTS = 1000

def epoch_millis():
    return int(time.time_ns() / 1000000)

def login(session, base_url, username, password):
    login_url = f"{base_url}/users/login"

    # Fetch the login page
    resp = session.get(login_url, timeout=30)
    resp.raise_for_status()

    # Parse the html in the response
    soup = BeautifulSoup(resp.text, "html.parser")

    # Find the csrf token
    csrf_token_element = soup.find("input", attrs={"name": "authenticity_token"})
    if not csrf_token_element or not csrf_token_element.get("value"):
        raise RuntimeError("Could not find the login CSRF token — is the site reachable?")

    login_payload = {
        "authenticity_token": csrf_token_element["value"],
        "user[login]": username,
        "user[password]": password,
        "user[remember_me]": "1",
        "commit": "Log In",
    }

    # Log in
    resp = session.post(login_url, data=login_payload, timeout=30)
    resp.raise_for_status()

    # We should be on a new page after a successful login
    if "/users/login" in resp.url or "Please try again" in resp.text:
        raise RuntimeError("Login failed — check your username/password.")

    # logged in successfully, session is in the Session object now
    return True


def sync(args):
    print(args)
    base_url = args.base_url.rstrip("/")
    password = args.password or os.environ.get("AO3_PASSWORD") or getpass.getpass("AO3 password: ")

    session = Session()
    session.headers["User-Agent"] = "ao3-history/1.0 (personal history backup)"

    print(f"Logging in as {args.username} at {base_url} ...")
    login(session, base_url, args.username, password)
    print("Logged in.")

    conn = connect(args.db)

    history_url = f"{base_url}/users/{args.username}/readings"
    current_page = 1
    current_time = epoch_millis()

    while True:
        remaining_ms = MIN_MILLIS_BETWEEN_REQUESTS - (epoch_millis() - current_time)
        if remaining_ms > 0:
            print(f"Sleeping for {remaining_ms}ms")
            time.sleep(remaining_ms / 1000)
        current_time = epoch_millis()

        resp = session.get(history_url, params={"page": current_page}, timeout=30)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        entries = soup.select("ol.reading li.blurb")

        if not entries:
            break

        for entry in entries:
            work = {
                "work_id": None,
                "title": None,
                "author": None,
                "url": None,
                "fandoms": "",
                "tags": "",
            }

            print(f"-----> {entry}")
            work_id = entry["id"]
            if not work_id:
                continue

            work["work_id"] = int(work_id.replace("work_", ""))
            title_element = entry.select_one("h4.heading a")
            if title_element is None:
                # Can't see this or maybe it's deleted
                continue

            work["title"] = entry.select_one("h4.heading a").get_text(strip=True)
            work["url"] = base_url + entry.select_one("h4.heading a").get("href")
            authors = list(map(lambda x: x.get_text(strip=True), entry.select("h4.heading a[rel=author]")))
            work["author"] = ", ".join(authors)
            fandoms = list(map(lambda x: x.get_text(strip=True), entry.select("h5.fandoms.heading a")))
            work["fandoms"] = ", ".join(fandoms)
            tags = list(map(lambda x: x.get_text(strip=True), entry.select("ul.tags li a.tag")))
            work["tags"] = ", ".join(tags)

            print(f"Inserting #{work}")
            upsert(conn, work)

        # Finished the page
        current_page += 1
    conn.close()
