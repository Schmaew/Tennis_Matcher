"""
expiration.py
================================================================
Background loop that auto-declines match requests sitting in
pending limbo. If one side accepted and the other never replied,
the accepter gets a push notification and a 🎾 หาคู่ใหม่ button.

Tunable via env vars (handy for testing):
    MATCH_EXPIRY_HOURS              — default 24
    EXPIRY_CHECK_INTERVAL_SECONDS   — default 3600 (one hour)

Production note: this uses a daemon thread inside the Flask process.
That's fine for dev / single-instance deployments. A real prod setup
would call `db.expire_stale_matches()` from a separate cron job.
================================================================
"""

import os
import threading
import time

from linebot.v3.messaging import MessagingApi, PushMessageRequest

import db
import messages as msg
from quick_reply import with_find_partner_button

EXPIRY_HOURS = float(os.getenv("MATCH_EXPIRY_HOURS", "24"))
CHECK_INTERVAL_SECONDS = float(os.getenv("EXPIRY_CHECK_INTERVAL_SECONDS", "3600"))


def _notify_one(line_api: MessagingApi, user_id: str) -> None:
    try:
        line_api.push_message(PushMessageRequest(
            to=user_id,
            messages=[with_find_partner_button(msg.MATCH_EXPIRED)],
        ))
    except Exception as e:
        print(f"[expiration] push failed for {user_id}: {e}")


def _process(line_api: MessagingApi) -> None:
    expired = db.expire_stale_matches(EXPIRY_HOURS)
    if not expired:
        return
    print(f"[expiration] expired {len(expired)} match(es)")
    for m in expired:
        # Only notify the side that had already accepted — they're the ones left hanging.
        if m["player_a_response"] == "accepted":
            _notify_one(line_api, m["player_a_id"])
        if m["player_b_response"] == "accepted":
            _notify_one(line_api, m["player_b_id"])


def _loop(line_api: MessagingApi) -> None:
    while True:
        try:
            _process(line_api)
        except Exception as e:
            print(f"[expiration] iteration failed: {e}")
        time.sleep(CHECK_INTERVAL_SECONDS)


def start_expiration_thread(line_api: MessagingApi) -> None:
    t = threading.Thread(target=_loop, args=(line_api,), daemon=True)
    t.start()
    print(f"[expiration] started: hours={EXPIRY_HOURS} interval={CHECK_INTERVAL_SECONDS}s")
