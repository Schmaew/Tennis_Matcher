"""
db.py
================================================================
Supabase queries for the bot. One function per question:

    get_player(line_user_id)           -> dict | None
    upsert_player(line_user_id, data)  -> None
    update_player(line_user_id, data)  -> None
    get_active_players()               -> list[dict]
    create_match(a_id, b_id)           -> int
    get_match(match_id)                -> dict | None
    respond_to_match(match_id, ...)    -> dict | None
    mark_introduced(match_id)          -> None
    get_all_players()                  -> list[dict]
    delete_player(line_user_id)        -> None

The student should NOT need to write raw SQL anywhere else in the
codebase — every database call goes through this file.
================================================================
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

_sb: Client = create_client(
    os.environ["SUPABASE_URL"],
    os.environ["SUPABASE_SERVICE_KEY"],
)

# Whitelist of columns the bot is allowed to UPDATE on the players table.
# Same defense the senior's repo uses (db.js -> ALLOWED_PLAYER_COLUMNS).
# Prevents a typo or malicious payload from writing to a column it shouldn't.
_ALLOWED_PLAYER_COLUMNS = {
    "nickname", "skill_level", "area",
    "status", "onboarding_step",
}


def _validate(data: dict) -> None:
    for key in data:
        if key not in _ALLOWED_PLAYER_COLUMNS:
            raise ValueError(f"Invalid player column: {key}")


# ---------- Players ----------

def get_player(line_user_id: str) -> dict | None:
    res = _sb.table("players").select("*").eq("line_user_id", line_user_id).execute()
    return res.data[0] if res.data else None


def upsert_player(line_user_id: str) -> None:
    """Create a player row if it doesn't exist yet (idempotent)."""
    if get_player(line_user_id):
        return
    _sb.table("players").insert({
        "line_user_id": line_user_id,
        "status": "onboarding",
        "onboarding_step": 0,
    }).execute()


def update_player(line_user_id: str, data: dict) -> None:
    if not data:
        return
    _validate(data)
    _sb.table("players").update(data).eq("line_user_id", line_user_id).execute()


def get_active_players() -> list[dict]:
    res = _sb.table("players").select("*").eq("status", "active").execute()
    return res.data or []


def get_all_players() -> list[dict]:
    res = _sb.table("players").select("*").order("registered_at", desc=True).execute()
    return res.data or []


def delete_player(line_user_id: str) -> None:
    """Full wipe — used by the `ลิงรีเซ็ต` cheat command for testing."""
    _sb.table("matches").delete().or_(
        f"player_a_id.eq.{line_user_id},player_b_id.eq.{line_user_id}"
    ).execute()
    _sb.table("players").delete().eq("line_user_id", line_user_id).execute()


# ---------- Matches ----------

def create_match(player_a_id: str, player_b_id: str) -> int:
    res = _sb.table("matches").insert({
        "player_a_id": player_a_id,
        "player_b_id": player_b_id,
    }).execute()
    return res.data[0]["id"]


def get_match(match_id: int) -> dict | None:
    res = _sb.table("matches").select("*").eq("id", match_id).execute()
    return res.data[0] if res.data else None


def respond_to_match(match_id: int, line_user_id: str, response: str) -> dict | None:
    """Record one side's accept/decline. Returns the updated row."""
    match = get_match(match_id)
    if not match:
        return None

    if match["player_a_id"] == line_user_id:
        column = "player_a_response"
    elif match["player_b_id"] == line_user_id:
        column = "player_b_response"
    else:
        return None  # caller is not in this match

    _sb.table("matches").update({column: response}).eq("id", match_id).execute()
    return get_match(match_id)


def mark_introduced(match_id: int) -> None:
    _sb.table("matches").update({"introduced": True}).eq("id", match_id).execute()
