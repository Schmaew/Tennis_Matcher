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
  -  Done. status = 'active'.

🎓 CUSTOMIZE: add or remove steps by editing _STEP_HANDLERS below.
   Each handler is one function: read the user's reply, save it,
   return the next message to send.
================================================================
"""

from linebot.v3.messaging import TextMessage

import db
import messages as msg
from quick_reply import build_quick_reply


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


# --- Public entry points ---------------------------------------

def start_onboarding(line_user_id: str) -> list[TextMessage]:
    """Called when a brand-new user adds the bot (follow event)."""
    db.upsert_player(line_user_id)
    db.update_player(line_user_id, {"status": "onboarding", "onboarding_step": 1})
    return [TextMessage(text=msg.WELCOME), _ask_nickname()]


def resume_onboarding(player: dict) -> TextMessage:
    """If the user dropped off mid-flow, re-ask the current question."""
    return _question_for_step(player["onboarding_step"])


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
        "status": "active",
        "onboarding_step": 0,  # reset; we use status='active' as the done marker
    })
    return [TextMessage(text=msg.ONBOARDING_DONE)]


# 🎓 CUSTOMIZE: register a new step here to add a new question.
_STEP_HANDLERS = {
    1: _step1_save_nickname,
    2: _step2_save_skill,
    3: _step3_save_area,
}


def _question_for_step(step: int) -> TextMessage:
    if step == 1:
        return _ask_nickname()
    if step == 2:
        return _ask_skill()
    if step == 3:
        return _ask_area()
    return TextMessage(text=msg.UNKNOWN)
