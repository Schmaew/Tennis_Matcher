"""
matching.py
================================================================
Player ↔ player matching.

Triggered by the user typing 'หาคู่'. The bot looks for an active
player in the same area with a similar skill level, creates a match
row, and sends both sides a quick-reply card asking "interested?".

Flow
----
    A: types "หาคู่"
        -> find_best_partner(A)
        -> create match row (id=42)
        -> push to A: "Found B! [✅ สนใจ] [❌ ไม่สะดวก]"  (tokens: accept_42 / decline_42)
        -> push to B: same card

    Either side taps a button:
        -> handle_match_response()
        -> if both accept -> mark introduced, reveal LINE IDs
        -> if either declines -> short ack, no intro

🎓 CUSTOMIZE: tune the scoring weights in `_score()` to change how
   "compatible" two players need to be. Add new criteria (preferred
   time, play style, etc.) by extending the score function and the
   players table schema.
================================================================
"""

from linebot.v3.messaging import TextMessage

import db
import messages as msg
from quick_reply import build_quick_reply

# Skill levels in order — used to compute skill-distance.
_SKILLS = ["beginner", "casual", "intermediate", "competitive"]


def find_best_partner(player: dict) -> dict | None:
    """
    Score every other active player against `player` and return the best.
    Returns None if no acceptable candidate exists.
    """
    candidates = [
        p for p in db.get_active_players()
        if p["line_user_id"] != player["line_user_id"]
    ]

    scored = [(_score(player, c), c) for c in candidates]
    scored = [s for s in scored if s[0] > 0]
    if not scored:
        return None

    scored.sort(key=lambda s: s[0], reverse=True)
    return scored[0][1]


def _score(a: dict, b: dict) -> int:
    """
    Compatibility score. Higher = better match.
    0 means "not a match" — caller filters these out.
    """
    score = 0

    # 🎓 CUSTOMIZE: same area is the strongest signal — bump or lower this weight.
    if a.get("area") and a["area"] == b.get("area"):
        score += 3

    # Skill: same level = +2, ±1 level = +1, further = disqualify.
    try:
        i_a = _SKILLS.index(a.get("skill_level"))
        i_b = _SKILLS.index(b.get("skill_level"))
    except ValueError:
        return 0  # one side hasn't set a skill yet
    diff = abs(i_a - i_b)
    if diff == 0:
        score += 2
    elif diff == 1:
        score += 1
    else:
        return 0

    return score


# --- Match invitation ------------------------------------------

def build_match_card(other: dict, match_id: int) -> TextMessage:
    """A card with two buttons: accept_<id> / decline_<id>."""
    return TextMessage(
        text=msg.match_invite(other),
        quick_reply=build_quick_reply([
            {"label": "✅ สนใจ",   "text": f"accept_{match_id}"},
            {"label": "❌ ไม่สะดวก", "text": f"decline_{match_id}"},
        ]),
    )


# --- Response handling -----------------------------------------

def handle_match_response(
    user_id: str, action: str, match_id: int,
) -> tuple[list[TextMessage], list[tuple[str, TextMessage]]]:
    """
    Apply an accept/decline. Returns (reply_to_caller, list_of_pushes).

    Each push is (target_user_id, message). The webhook handler turns
    `reply_to_caller` into a `reply_message()` and `pushes` into
    `push_message()` calls.
    """
    match = db.get_match(match_id)
    if not match:
        return ([TextMessage(text="⚠️ ไม่พบคู่นี้แล้ว")], [])

    # SECURITY: only let participants of this match touch its state.
    if user_id not in (match["player_a_id"], match["player_b_id"]):
        return ([], [])

    # SECURITY: stale tap after both sides already introduced — ignore.
    if match["introduced"]:
        return ([], [])

    response = "accepted" if action == "accept" else "declined"
    updated = db.respond_to_match(match_id, user_id, response)
    if not updated:
        return ([], [])

    if action == "decline":
        return ([TextMessage(text=msg.MATCH_DECLINED)], [])

    # Acknowledged accept — but partner hasn't responded yet.
    if not (
        updated["player_a_response"] == "accepted"
        and updated["player_b_response"] == "accepted"
    ):
        return ([TextMessage(text=msg.MATCH_ACCEPTED_WAIT)], [])

    # Both accepted — introduce them.
    db.mark_introduced(match_id)
    a = db.get_player(updated["player_a_id"])
    b = db.get_player(updated["player_b_id"])

    # Reply to whoever just clicked; push to the other.
    other = b if user_id == a["line_user_id"] else a
    self_ = a if user_id == a["line_user_id"] else b
    return (
        [TextMessage(text=msg.match_introduction(self_["nickname"], other["nickname"], other["line_user_id"]))],
        [(other["line_user_id"], TextMessage(text=msg.match_introduction(other["nickname"], self_["nickname"], self_["line_user_id"])))],
    )
