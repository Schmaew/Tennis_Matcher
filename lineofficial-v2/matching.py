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

import os

from linebot.v3.messaging import TextMessage, PushMessageRequest

import db
import messages as msg
from quick_reply import build_quick_reply, with_find_partner_button, with_skip_button

PARALLEL_MATCH_N = int(os.getenv("PARALLEL_MATCH_N", "1"))

# Skill levels in order — used to compute skill-distance.
_SKILLS = ["beginner", "casual", "intermediate", "competitive"]


def find_best_partner(player: dict) -> dict | None:
    """Score all candidates against `player`; return the single best, or None."""
    top = find_top_n_partners(player, n=1)
    return top[0] if top else None


def find_top_n_partners(player: dict, n: int) -> list[dict]:
    """Score all candidates against `player`; return up to `n` best, highest score first."""
    candidates = [
        p for p in db.get_active_players()
        if p["line_user_id"] != player["line_user_id"]
    ]
    skip_counts = db.get_skip_counts_for(player["line_user_id"])
    scored = [(_score(player, c, skip_counts), c) for c in candidates]
    scored = [s for s in scored if s[0] > 0]
    scored.sort(key=lambda s: s[0], reverse=True)
    return [c for _, c in scored[:n]]


def initiate_matches(player: dict, n: int | None = None) -> list[tuple[dict, int]]:
    """
    Pick the top-N candidates, create a match row for each, and return
    list of (candidate, match_id). Empty list if no compatible candidates.
    Caller is responsible for actually sending the messages.
    """
    n = n if n is not None else PARALLEL_MATCH_N
    pairs: list[tuple[dict, int]] = []
    for c in find_top_n_partners(player, n=n):
        match_id = db.create_match(player["line_user_id"], c["line_user_id"])
        pairs.append((c, match_id))
    return pairs


def _score(a: dict, b: dict, skip_counts: dict[str, int] | None = None) -> int:
    """
    Compatibility score. Higher = better match.
    0 means "not a match" — caller filters these out.

    `skip_counts` is {other_user_id: how_many_times_A_has_skipped_them}.
    Three+ skips disqualifies the pair; each skip otherwise costs 2 points.
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

    # Skip penalty.
    if skip_counts:
        skips = skip_counts.get(b["line_user_id"], 0)
        if skips >= 3:
            return 0
        score -= 2 * skips

    return score if score > 0 else 0


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
        # If the other side had already accepted, notify them so they're not left hanging.
        is_player_a = (user_id == match["player_a_id"])
        other_id = match["player_b_id"] if is_player_a else match["player_a_id"]
        other_response = (
            updated["player_b_response"] if is_player_a else updated["player_a_response"]
        )
        pushes = []
        if other_response == "accepted":
            pushes.append((other_id, with_find_partner_button(msg.MATCH_PARTNER_DECLINED)))
        return ([with_find_partner_button(msg.MATCH_DECLINED)], pushes)

    # Acknowledged accept — but partner hasn't responded yet.
    if not (
        updated["player_a_response"] == "accepted"
        and updated["player_b_response"] == "accepted"
    ):
        return ([with_skip_button(msg.MATCH_ACCEPTED_WAIT, match_id)], [])

    # Both accepted — introduce them.
    db.mark_introduced(match_id)
    a = db.get_player(updated["player_a_id"])
    b = db.get_player(updated["player_b_id"])

    # Reply to whoever just clicked; push to the other.
    other = b if user_id == a["line_user_id"] else a
    self_ = a if user_id == a["line_user_id"] else b

    # Auto-cancel any other parallel invites involving A or B, notify those
    # candidates so they're not left waiting on a match that can't happen.
    cancel_pushes = (
        _cancel_other_invites_for(a["line_user_id"], match_id)
        + _cancel_other_invites_for(b["line_user_id"], match_id)
    )

    intro_to_other = (other["line_user_id"], with_find_partner_button(
        msg.match_introduction(other["nickname"], self_["nickname"], self_.get("line_basic_id"))
    ))
    return (
        [with_find_partner_button(msg.match_introduction(self_["nickname"], other["nickname"], other.get("line_basic_id")))],
        [intro_to_other] + cancel_pushes,
    )


def handle_match_skip(
    user_id: str, match_id: int,
) -> tuple[list[TextMessage], list[tuple[str, TextMessage]]]:
    """
    User taps ⏭️ ข้าม on the 'waiting for partner' message:
      1. Flip their response to declined (frees the match)
      2. Increment match_skips[user -> other_user]
      3. If the other side had already accepted, push them MATCH_PARTNER_DECLINED.
    """
    match = db.get_match(match_id)
    if not match:
        return ([TextMessage(text="⚠️ ไม่พบคู่นี้แล้ว")], [])
    if user_id not in (match["player_a_id"], match["player_b_id"]):
        return ([], [])
    if match["introduced"]:
        return ([], [])

    is_player_a = (user_id == match["player_a_id"])
    other_id = match["player_b_id"] if is_player_a else match["player_a_id"]
    other_response = match["player_b_response"] if is_player_a else match["player_a_response"]

    db.respond_to_match(match_id, user_id, "declined")
    db.record_skip(user_id, other_id)

    pushes: list[tuple[str, TextMessage]] = []
    if other_response == "accepted":
        pushes.append((other_id, with_find_partner_button(msg.MATCH_PARTNER_DECLINED)))
    return ([with_find_partner_button(msg.MATCH_SKIPPED_ACK)], pushes)


def _cancel_other_invites_for(self_user_id: str, current_match_id: int) -> list[tuple[str, TextMessage]]:
    """
    Decline all other live (non-introduced, non-declined) matches involving
    `self_user_id` and return push notifications for the OTHER side of each.
    """
    pushes: list[tuple[str, TextMessage]] = []
    seen_targets: set[str] = set()
    for m in db.get_other_active_matches(self_user_id, current_match_id):
        db.cancel_match(m["id"])
        other_id = m["player_b_id"] if m["player_a_id"] == self_user_id else m["player_a_id"]
        if other_id in seen_targets:
            continue  # avoid pushing the same MATCH_CANCELED_OTHER twice to the same user
        seen_targets.add(other_id)
        pushes.append((other_id, with_find_partner_button(msg.MATCH_CANCELED_OTHER)))
    return pushes


# --- Waiting-queue trigger -------------------------------------

def try_match_from_queue(line_api, new_active_user: dict) -> None:
    """
    Called when `new_active_user` just transitioned to status='active'.
    Walk the FIFO queue and, if any waiter is compatible with the new user,
    trigger a parallel match for that waiter (and dequeue them).
    """
    new_user_id = new_active_user["line_user_id"]
    for entry in db.get_waiting_queue():
        waiter_id = entry["line_user_id"]
        if waiter_id == new_user_id:
            db.dequeue_waiting(waiter_id)
            continue
        waiter = db.get_player(waiter_id)
        if not waiter or waiter.get("status") != "active":
            db.dequeue_waiting(waiter_id)
            continue
        if _score(waiter, new_active_user) == 0:
            continue  # not compatible — keep them in the queue

        pairs = initiate_matches(waiter)
        if not pairs:
            continue  # extremely unlikely (we just confirmed at least new_user is compatible)
        db.dequeue_waiting(waiter_id)

        # Notify the waiter (push — they're not in chat right now)
        cards = [build_match_card(c, mid) for c, mid in pairs]
        line_api.push_message(PushMessageRequest(
            to=waiter_id,
            messages=([TextMessage(text=msg.match_parallel_sent(len(pairs)))] + cards)[:5],
        ))
        # And push the invite to each chosen candidate
        for c, mid in pairs:
            line_api.push_message(PushMessageRequest(
                to=c["line_user_id"],
                messages=[build_match_card(waiter, mid)],
            ))
        return  # one waiter matched per trigger — keep it simple
