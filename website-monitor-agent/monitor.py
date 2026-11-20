#!/usr/bin/env python3
"""Website A -> Website B -> Website A monitoring flow."""

import os
import sys
import time
import smtplib
import urllib.request
import urllib.error
from email.message import EmailMessage
from datetime import datetime, timezone

TIMEOUT = int(os.getenv("CHECK_TIMEOUT_SECONDS", "15"))
A_URL = os.getenv("WEBSITE_A_URL", "https://ss-auction-server-3.onrender.com/").strip()
B_URL = os.getenv("WEBSITE_B_URL", "https://ss-auction-server-2.onrender.com/").strip()


def check_site(url: str):
    if not url:
        return False, "URL is not configured"
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "FreeWebsiteMonitor/1.0"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            code = response.status
            return (200 <= code < 400), f"HTTP {code}"
    except urllib.error.HTTPError as exc:
        # HTTP errors are failures, but report their status explicitly.
        return False, f"HTTP {exc.code}"
    except Exception as exc:
        return False, f"{type(exc).__name__}: {exc}"


def send_alert(subject: str, body: str):
    sender = os.environ["SMTP_EMAIL"]
    password = os.environ["SMTP_APP_PASSWORD"]
    recipient = os.environ["ALERT_TO_EMAIL"]

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient
    msg.set_content(body)

    with smtplib.SMTP("smtp.gmail.com", 587, timeout=30) as smtp:
        smtp.starttls()
        smtp.login(sender, password)
        smtp.send_message(msg)


def main():
    if not A_URL or not B_URL:
        print("ERROR: Website URLs are empty. Set WEBSITE_A_URL and WEBSITE_B_URL, or use the built-in SS AUCTION defaults.")
        sys.exit(2)
    for label, url in (("WEBSITE_A_URL", A_URL), ("WEBSITE_B_URL", B_URL)):
        if not url.startswith(("http://", "https://")):
            print(f"ERROR: {label} must start with http:// or https:// (configured value is invalid).")
            sys.exit(2)

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    print(f"Monitor run started at {timestamp}")

    a1_ok, a1_result = check_site(A_URL)
    print(f"Website A initial check: {'UP' if a1_ok else 'DOWN'} — {a1_result}")
    if a1_ok:
        print("Website A is healthy. No further checks needed.")
        return

    b_ok, b_result = check_site(B_URL)
    print(f"Website B check: {'UP' if b_ok else 'DOWN'} — {b_result}")

    if not b_ok:
        body = (
            f"Website monitoring alert at {timestamp}.\n\n"
            f"Website A failed its initial check: {A_URL}\nResult: {a1_result}\n\n"
            f"Website B also failed: {B_URL}\nResult: {b_result}\n\n"
            "As requested, Website A was NOT checked again after Website B failed."
        )
        send_alert("ALERT: Website A and Website B are down", body)
        print("Alert email sent. Website A was not checked again.")
        return

    # B is working; now check A one final time.
    time.sleep(2)
    a2_ok, a2_result = check_site(A_URL)
    print(f"Website A retry: {'UP' if a2_ok else 'DOWN'} — {a2_result}")

    if a2_ok:
        print("Website A recovered. No email alert.")
        return

    body = (
        f"Website monitoring alert at {timestamp}.\n\n"
        f"Website A failed initially: {A_URL}\nResult: {a1_result}\n\n"
        f"Website B is working: {B_URL}\nResult: {b_result}\n\n"
        f"Website A failed again on the final check.\nResult: {a2_result}"
    )
    send_alert("ALERT: Website A is still down (Website B is up)", body)
    print("Alert email sent: Website B works, Website A remains down.")


if __name__ == "__main__":
    main()
