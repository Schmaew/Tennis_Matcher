"""
quick_reply.py
================================================================
Helpers for LINE quick-reply buttons.

A "quick reply" is a row of buttons under the bot's message that, when
tapped, sends a message back to the bot as if the user typed it.

Why this matters
----------------
Most bots don't want the user typing free text — buttons make the
flow predictable. The bot sends button labels the user sees, plus
a hidden `text` payload that the bot regex-matches in server.py to
decide what to do.

Pattern (mirrors the senior's `quickReply` helper in onboarding.js):

    options = [
        {"label": "🏃 Singles", "text": "style_singles"},
        {"label": "👥 Doubles", "text": "style_doubles"},
    ]
    msg = TextMessage(
        text="Pick a style",
        quick_reply=build_quick_reply(options),
    )

🎓 CUSTOMIZE: change button labels (what user sees) by editing the
   strings passed in. Change tokens (what bot receives) carefully —
   server.py uses regex to match them.
================================================================
"""

from linebot.v3.messaging import (
    QuickReply,
    QuickReplyItem,
    MessageAction,
    TextMessage,
)


def build_quick_reply(options: list[dict]) -> QuickReply:
    """
    Build a QuickReply from a list of {label, text} dicts.
    LINE caps each label at 20 chars — we slice to be safe.
    """
    items = [
        QuickReplyItem(
            action=MessageAction(label=opt["label"][:20], text=opt["text"]),
        )
        for opt in options
    ]
    return QuickReply(items=items)


def with_find_partner_button(text: str) -> TextMessage:
    """Wrap a plain message in a TextMessage that carries a 'หาคู่ใหม่' quick-reply."""
    return TextMessage(
        text=text,
        quick_reply=build_quick_reply([
            {"label": "🎾 หาคู่ใหม่", "text": "หาคู่"},
        ]),
    )


def with_skip_button(text: str, match_id: int) -> TextMessage:
    """Wrap a 'waiting for the other side' message with an ⏭️ ข้าม button."""
    return TextMessage(
        text=text,
        quick_reply=build_quick_reply([
            {"label": "⏭️ ข้าม", "text": f"skip_{match_id}"},
        ]),
    )
