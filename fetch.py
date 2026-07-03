import getpass
import os

from bs4 import BeautifulSoup

from requests import Session

from db import connect


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

    print("Sync not implemented yet.")
