"""
server.py
================================================================
Flask app: webhook + admin dashboard.

Webhook flow
------------
LINE -> POST /webhook (with X-Line-Signature header)
  -> verify signature
  -> for each event:
       follow              -> start_onboarding()
       message (text):
         user is brand new          -> start_onboarding()
         user is mid-onboarding     -> handle_onboarding_message()
         user is active and typed:
           accept_<id> / decline_<id>  -> matching.handle_match_response()
           หาคู่                        -> find + send match card
           สถานะ                       -> player_status()
           หยุด / เริ่ม                  -> toggle status
           ลิงรีเซ็ต                    -> wipe + restart onboarding
           anything else              -> hint message

Run
---
    python server.py
    -> http://localhost:5001/webhook
    -> http://localhost:5001/admin (or /<ADMIN_PATH_SECRET>/admin)
================================================================
"""

import os
import re
from flask import Flask, request, abort

from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    PushMessageRequest,
    TextMessage,
)
from linebot.v3.webhooks import (
    MessageEvent,
    FollowEvent,
    TextMessageContent,
)
from dotenv import load_dotenv

import db
import messages as msg
import onboarding
import matching
from admin import admin_bp, admin_base_path

load_dotenv()

# --- App + clients ---------------------------------------------

app = Flask(__name__)
app.register_blueprint(admin_bp)

handler = WebhookHandler(os.environ["LINE_CHANNEL_SECRET"])

line_api = MessagingApi(
    ApiClient(Configuration(access_token=os.environ["LINE_CHANNEL_ACCESS_TOKEN"]))
)


# --- Webhook entry ---------------------------------------------

@app.route("/webhook", methods=["POST"])
def webhook():
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"


# --- Event handlers --------------------------------------------

@handler.add(FollowEvent)
def on_follow(event):
    """User just added the bot as friend — kick off onboarding."""
    user_id = event.source.user_id
    replies = onboarding.start_onboarding(user_id)
    _reply(event.reply_token, replies)


@handler.add(MessageEvent, message=TextMessageContent)
def on_text_message(event):
    user_id = event.source.user_id
    text = event.message.text.strip()

    # 🎓 CUSTOMIZE: add new global commands here.
    if text == "ลิงรีเซ็ต":
        db.delete_player(user_id)
        replies = onboarding.start_onboarding(user_id)
        return _reply(event.reply_token, replies)

    player = db.get_player(user_id)

    # Brand-new user (e.g. user joined while bot was down) — start onboarding.
    if not player:
        replies = onboarding.start_onboarding(user_id)
        return _reply(event.reply_token, replies)

    # Mid-onboarding — feed the answer to the state machine.
    if player["status"] == "onboarding":
        replies = onboarding.handle_onboarding_message(player, text)
        if replies:
            return _reply(event.reply_token, replies)
        return _reply(event.reply_token, [onboarding.resume_onboarding(player)])

    # --- Quick-reply tokens (must come BEFORE plain-text commands) ---
    # Same regex pattern the senior's repo uses (handlers.js).
    m = re.match(r"^(accept|decline)_(\d+)$", text)
    if m:
        action, match_id = m.group(1), int(m.group(2))
        replies, pushes = matching.handle_match_response(user_id, action, match_id)
        if replies:
            _reply(event.reply_token, replies)
        for target_id, push_msg in pushes:
            line_api.push_message(PushMessageRequest(to=target_id, messages=[push_msg]))
        return

    # --- Plain-text commands for active players ---
    if text == "สถานะ":
        return _reply(event.reply_token, [TextMessage(text=msg.player_status(player))])

    if text == "หาคู่":
        return _find_partner(event.reply_token, player)

    if text == "หยุด":
        db.update_player(user_id, {"status": "paused"})
        return _reply(event.reply_token, [TextMessage(text=msg.PAUSED)])

    if text == "เริ่ม":
        db.update_player(user_id, {"status": "active"})
        return _reply(event.reply_token, [TextMessage(text=msg.RESUMED)])

    # 🎓 CUSTOMIZE: add new commands above this line.
    return _reply(event.reply_token, [TextMessage(text=msg.UNKNOWN)])


# --- Helpers ---------------------------------------------------

def _reply(reply_token: str, messages: list[TextMessage]) -> None:
    """LINE caps replies at 5 messages — slice defensively."""
    if not messages:
        return
    line_api.reply_message(
        ReplyMessageRequest(reply_token=reply_token, messages=messages[:5])
    )


def _find_partner(reply_token: str, player: dict) -> None:
    other = matching.find_best_partner(player)
    if not other:
        return _reply(reply_token, [TextMessage(text=msg.MATCH_NO_CANDIDATES)])

    match_id = db.create_match(player["line_user_id"], other["line_user_id"])

    # Reply to caller, push to the other side.
    _reply(reply_token, [matching.build_match_card(other, match_id)])
    line_api.push_message(PushMessageRequest(
        to=other["line_user_id"],
        messages=[matching.build_match_card(player, match_id)],
    ))


# --- Entry point -----------------------------------------------

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5001))
    print(f"Tennis Matcher Bot v2 listening on http://localhost:{port}")
    print(f"  webhook: http://localhost:{port}/webhook")
    print(f"  admin:   http://localhost:{port}{admin_base_path()}")
    app.run(port=port, debug=False)
