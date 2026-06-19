"""
seed_mock_data.py
================================================================
Insert ~15 fake players + a handful of matches + some queue entries
so the admin dashboard has something interesting to show.

Every fake row has a `line_user_id` prefixed with 'mock_' so this
script and `clear_mock_data.py` can both find and remove them
without touching real users.

Run:
    cd lineofficial-v2
    python3 scripts/seed_mock_data.py
================================================================
"""

import os
import random
import sys
from pathlib import Path

# Allow `import db` from the parent dir.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

import db  # noqa: E402

NICKNAMES = [
    "Nong", "Ploy", "Bird", "Earth", "Fern", "Gun", "Ice", "Jay",
    "Kao", "Lek", "Mint", "Nan", "Oat", "Pim", "Tay",
]
SKILLS = ["beginner", "casual", "intermediate", "competitive"]
AREAS = [
    "บางนา / ศรีนครินทร์",
    "สุขุมวิท / ทองหล่อ",
    "รามคำแหง / บางกะปิ",
    "สีลม / สาทร / ลุมพินี",
]


def seed_players() -> list[str]:
    random.seed(42)  # deterministic — same names get same attributes each run
    user_ids: list[str] = []
    for i, nick in enumerate(NICKNAMES, start=1):
        uid = f"mock_{i:03d}"
        user_ids.append(uid)
        # Skip if already present from a previous seed run.
        if db.get_player(uid):
            continue
        db._sb.table("players").insert({
            "line_user_id": uid,
            "nickname": nick,
            "skill_level": random.choice(SKILLS),
            "area": random.choice(AREAS),
            "line_basic_id": f"{nick.lower()}_tennis",
            "status": "active",
            "onboarding_step": 0,
        }).execute()
        print(f"  + player {uid:9} {nick}")
    return user_ids


def seed_matches(user_ids: list[str]) -> None:
    """Create a few matches across the mock users to exercise the matcher."""
    random.seed(7)
    pairs = [
        (user_ids[0], user_ids[1], "accepted", "accepted", True),    # introduced
        (user_ids[2], user_ids[3], "accepted", "pending",  False),   # waiting
        (user_ids[4], user_ids[5], "declined", "accepted", False),   # one declined
        (user_ids[6], user_ids[7], "pending",  "pending",  False),   # fresh
        (user_ids[8], user_ids[9], "accepted", "accepted", True),    # introduced
    ]
    for a, b, ra, rb, intro in pairs:
        row = db._sb.table("matches").insert({
            "player_a_id": a,
            "player_b_id": b,
            "player_a_response": ra,
            "player_b_response": rb,
            "introduced": intro,
        }).execute()
        mid = row.data[0]["id"]
        print(f"  + match {mid:3} {a} <-> {b} (a={ra}, b={rb}, intro={intro})")


def seed_queue(user_ids: list[str]) -> None:
    """Put the last 3 mock users into the waiting queue."""
    for uid in user_ids[-3:]:
        db.enqueue_waiting(uid)
        print(f"  + queued {uid}")


def main() -> None:
    print("Seeding players...")
    uids = seed_players()
    print(f"\nSeeding matches across {len(uids)} mock players...")
    try:
        seed_matches(uids)
    except Exception as e:
        print(f"  ! match seed skipped: {e}")
    print("\nSeeding waiting queue...")
    try:
        seed_queue(uids)
    except Exception as e:
        print(f"  ! queue seed skipped (did you run add_waiting_queue.sql?): {e}")
    print("\nDone. Refresh the admin dashboard to see them.")


if __name__ == "__main__":
    main()
