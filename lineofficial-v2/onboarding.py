"""
onboarding.py
================================================================
Onboarding state machine.

Each player has an `onboarding_step` integer in the database.
A user reply moves them from step N to step N+1. Once at the
final step, status flips from 'onboarding' to 'active'.

Steps
  0  Just added the bot. Send welcome.
  1  Asked for nickname. Waiting for free-text reply.
  2  Asked for skill level. Waiting for one of 4 quick-reply tokens.
  3  Asked for area. Waiting for one of N quick-reply tokens.
  4  Asked for LINE Basic ID. Waiting for free-text reply.
  5  Sent self-profile link; waiting for "ใช่/ไม่ใช่" confirmation.
  -  Done. status = 'active'.

🎓 CUSTOMIZE: add or remove steps by editing _STEP_HANDLERS below.
   Each handler is one function: read the user's reply, save it,
   return the next message to send.
================================================================
"""

import re

from linebot.v3.messaging import TextMessage

import db
import messages as msg
from quick_reply import build_quick_reply, with_find_partner_button

# LINE Basic ID: 4-20 chars, lowercase letters, digits, '.', '-', '_'.
_LINE_BASIC_ID_RE = re.compile(r"^[a-z0-9._-]{4,20}$")


# --- Question builders -----------------------------------------

def _ask_nickname() -> TextMessage:
    return TextMessage(text=msg.Q_NICKNAME)


def _ask_skill() -> TextMessage:
    return TextMessage(
        text=msg.Q_SKILL,
        quick_reply=build_quick_reply([
            {"label": label, "text": code}
            for code, label in msg.SKILL_LABELS.items()
        ]),
    )


def _ask_area() -> TextMessage:
    return TextMessage(
        text=msg.Q_AREA,
        quick_reply=build_quick_reply([
            {"label": area, "text": area} for area in msg.AREA_OPTIONS
        ]),
    )


def _ask_line_basic_id() -> TextMessage:
    return TextMessage(text=msg.Q_LINE_BASIC_ID)


def _ask_confirm_basic_id(basic_id: str) -> TextMessage:
    return TextMessage(
        text=msg.confirm_line_basic_id(basic_id),
        quick_reply=build_quick_reply([
            {"label": msg.CONFIRM_YES, "text": msg.CONFIRM_YES},
            {"label": msg.CONFIRM_NO,  "text": msg.CONFIRM_NO},
        ]),
    )


def _normalize_basic_id(text: str) -> str | None:
    """Strip whitespace + leading '@', lowercase. Return None if invalid."""
    cleaned = text.strip().lstrip("@").lower()
    return cleaned if _LINE_BASIC_ID_RE.match(cleaned) else None


# --- Public entry points ---------------------------------------

def start_onboarding(line_user_id: str) -> list[TextMessage]:
    """Called when a brand-new user adds the bot (follow event)."""
    db.upsert_player(line_user_id)
    db.update_player(line_user_id, {"status": "onboarding", "onboarding_step": 1})
    return [TextMessage(text=msg.WELCOME), _ask_nickname()]


def resume_onboarding(player: dict) -> TextMessage:
    """If the user dropped off mid-flow, re-ask the current question."""
    step = player["onboarding_step"]
    if step == 5:
        stored = player.get("line_basic_id")
        return _ask_confirm_basic_id(stored) if stored else _ask_line_basic_id()
    return _question_for_step(step)


def handle_onboarding_message(player: dict, text: str) -> list[TextMessage] | None:
    """
    Process the user's reply to the question we last asked.
    Returns the next message(s) to send, or None if input was invalid.
    """
    step = player["onboarding_step"]
    handler = _STEP_HANDLERS.get(step)
    if not handler:
        return None
    return handler(player, text)


# --- Per-step handlers -----------------------------------------

def _step1_save_nickname(player: dict, text: str) -> list[TextMessage]:
    nickname = text.strip()[:50]
    if not nickname:
        return [_ask_nickname()]
    db.update_player(player["line_user_id"], {
        "nickname": nickname,
        "onboarding_step": 2,
    })
    return [_ask_skill()]


def _step2_save_skill(player: dict, text: str) -> list[TextMessage]:
    if text not in msg.SKILL_LABELS:
        return [_ask_skill()]  # invalid input — re-ask
    db.update_player(player["line_user_id"], {
        "skill_level": text,
        "onboarding_step": 3,
    })
    return [_ask_area()]


def _step3_save_area(player: dict, text: str) -> list[TextMessage]:
    if text not in msg.AREA_OPTIONS:
        return [_ask_area()]  # invalid input — re-ask
    db.update_player(player["line_user_id"], {
        "area": text,
        "onboarding_step": 4,
    })
    return [_ask_line_basic_id()]


def _step4_save_line_basic_id(player: dict, text: str) -> list[TextMessage]:
    basic_id = _normalize_basic_id(text)
    if not basic_id:
        return [TextMessage(text=msg.Q_LINE_BASIC_ID_INVALID)]
    db.update_player(player["line_user_id"], {
        "line_basic_id": basic_id,
        "onboarding_step": 5,
    })
    return [_ask_confirm_basic_id(basic_id)]


def _step5_confirm_basic_id(player: dict, text: str) -> list[TextMessage]:
    if text == msg.CONFIRM_YES:
        db.update_player(player["line_user_id"], {
            "status": "active",
            "onboarding_step": 0,  # reset; we use status='active' as the done marker
        })
        return [with_find_partner_button(msg.ONBOARDING_DONE)]
    if text == msg.CONFIRM_NO:
        db.update_player(player["line_user_id"], {
            "line_basic_id": None,
            "onboarding_step": 4,
        })
        return [_ask_line_basic_id()]
    # Anything else — re-show the confirm question with the stored id
    stored = player.get("line_basic_id")
    return [_ask_confirm_basic_id(stored)] if stored else [_ask_line_basic_id()]


# 🎓 CUSTOMIZE: register a new step here to add a new question.
_STEP_HANDLERS = {
    1: _step1_save_nickname,
    2: _step2_save_skill,
    3: _step3_save_area,
    4: _step4_save_line_basic_id,
    5: _step5_confirm_basic_id,
}


def _question_for_step(step: int) -> TextMessage:
    if step == 1:
        return _ask_nickname()
    if step == 2:
        return _ask_skill()
    if step == 3:
        return _ask_area()
    if step == 4:
        return _ask_line_basic_id()
    return TextMessage(text=msg.UNKNOWN)
