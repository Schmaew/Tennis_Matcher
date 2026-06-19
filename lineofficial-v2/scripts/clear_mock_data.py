"""
clear_mock_data.py
================================================================
Remove everything `seed_mock_data.py` inserted. Only deletes rows
whose `line_user_id` starts with 'mock_' — real users are safe.
================================================================
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

import db  # noqa: E402


def main() -> None:
    res = db._sb.table("players").select("line_user_id").like("line_user_id", "mock_%").execute()
    uids = [r["line_user_id"] for r in (res.data or [])]
    if not uids:
        print("No mock players found.")
        return
    print(f"Removing {len(uids)} mock players...")
    for uid in uids:
        # delete_player also cleans up matches involving this user
        db.delete_player(uid)
        # In case any are still in the queue (delete_player doesn't touch it)
        db.dequeue_waiting(uid)
        print(f"  - {uid}")
    print("Done.")


if __name__ == "__main__":
    main()
