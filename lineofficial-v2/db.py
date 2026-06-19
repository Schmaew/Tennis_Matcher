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
from datetime import datetime, timedelta, timezone
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
    "nickname", "skill_level", "area", "line_basic_id",
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


def get_other_active_matches(line_user_id: str, exclude_match_id: int) -> list[dict]:
    """
    Matches involving `line_user_id` that aren't introduced yet and where
    neither side has declined — i.e., still live invitations the user could
    end up paired with. Excludes the match they just resolved.
    """
    res = (
        _sb.table("matches")
        .select("*")
        .eq("introduced", False)
        .neq("id", exclude_match_id)
        .neq("player_a_response", "declined")
        .neq("player_b_response", "declined")
        .or_(f"player_a_id.eq.{line_user_id},player_b_id.eq.{line_user_id}")
        .execute()
    )
    return res.data or []


def cancel_match(match_id: int) -> None:
    """Force-decline any non-declined side of a non-introduced match."""
    m = get_match(match_id)
    if not m or m["introduced"]:
        return
    updates = {}
    if m["player_a_response"] != "declined":
        updates["player_a_response"] = "declined"
    if m["player_b_response"] != "declined":
        updates["player_b_response"] = "declined"
    if updates:
        _sb.table("matches").update(updates).eq("id", match_id).execute()


# ---------- Waiting queue (FIFO) ----------

def enqueue_waiting(line_user_id: str) -> None:
    """Add to queue. Silently no-op if user is already queued."""
    try:
        _sb.table("waiting_queue").insert({"line_user_id": line_user_id}).execute()
    except Exception:
        # UNIQUE constraint — already in the queue.
        pass


def dequeue_waiting(line_user_id: str) -> None:
    _sb.table("waiting_queue").delete().eq("line_user_id", line_user_id).execute()


def get_waiting_queue() -> list[dict]:
    """Queue rows ordered oldest-first (FIFO)."""
    res = _sb.table("waiting_queue").select("*").order("queued_at", desc=False).execute()
    return res.data or []


# ---------- Skip tracking (lower priority for skipped pairs) ----------

def record_skip(skipper_id: str, skipped_id: str) -> None:
    """Increment skip count for (skipper -> skipped). Insert if missing."""
    res = (
        _sb.table("match_skips")
        .select("count")
        .eq("skipper_id", skipper_id)
        .eq("skipped_id", skipped_id)
        .execute()
    )
    now = datetime.now(timezone.utc).isoformat()
    if res.data:
        new_count = (res.data[0]["count"] or 0) + 1
        (
            _sb.table("match_skips")
            .update({"count": new_count, "updated_at": now})
            .eq("skipper_id", skipper_id)
            .eq("skipped_id", skipped_id)
            .execute()
        )
    else:
        _sb.table("match_skips").insert({
            "skipper_id": skipper_id,
            "skipped_id": skipped_id,
            "count": 1,
            "updated_at": now,
        }).execute()


def get_skip_counts_for(skipper_id: str) -> dict[str, int]:
    """Return {skipped_user_id: count} for everyone this user has skipped."""
    try:
        res = (
            _sb.table("match_skips")
            .select("skipped_id, count")
            .eq("skipper_id", skipper_id)
            .execute()
        )
    except Exception:
        return {}  # table not migrated yet
    return {r["skipped_id"]: r["count"] for r in (res.data or [])}


def get_all_skips() -> list[dict]:
    try:
        res = _sb.table("match_skips").select("*").order("count", desc=True).execute()
        return res.data or []
    except Exception:
        return []


def get_matches_for(line_user_id: str) -> list[dict]:
    res = (
        _sb.table("matches")
        .select("*")
        .or_(f"player_a_id.eq.{line_user_id},player_b_id.eq.{line_user_id}")
        .order("suggested_at", desc=True)
        .execute()
    )
    return res.data or []


def get_skips_involving(line_user_id: str) -> tuple[list[dict], list[dict]]:
    """Return (skips_user_made, skips_made_against_user)."""
    try:
        made = (
            _sb.table("match_skips")
            .select("*")
            .eq("skipper_id", line_user_id)
            .order("count", desc=True)
            .execute()
            .data
            or []
        )
        received = (
            _sb.table("match_skips")
            .select("*")
            .eq("skipped_id", line_user_id)
            .order("count", desc=True)
            .execute()
            .data
            or []
        )
    except Exception:
        return [], []
    return made, received


def expire_stale_matches(hours: float = 24) -> list[dict]:
    """
    Find non-introduced matches older than `hours` that still have at least
    one pending response, flip those pending responses to 'declined', and
    return the ORIGINAL (pre-update) match rows so the caller can decide
    who to notify based on who had already accepted.
    """
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
    res = (
        _sb.table("matches")
        .select("*")
        .eq("introduced", False)
        .lt("suggested_at", cutoff)
        .or_("player_a_response.eq.pending,player_b_response.eq.pending")
        .execute()
    )
    stale = res.data or []
    for m in stale:
        updates = {}
        if m["player_a_response"] == "pending":
            updates["player_a_response"] = "declined"
        if m["player_b_response"] == "pending":
            updates["player_b_response"] = "declined"
        if updates:
            _sb.table("matches").update(updates).eq("id", m["id"]).execute()
    return stale
