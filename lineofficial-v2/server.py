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
import expiration
from admin import admin_bp, admin_base_path
from quick_reply import with_find_partner_button

load_dotenv()

# --- App + clients ---------------------------------------------

app = Flask(__name__)
app.register_blueprint(admin_bp)

handler = WebhookHandler(os.environ["LINE_CHANNEL_SECRET"])

line_api = MessagingApi(
    ApiClient(Configuration(access_token=os.environ["LINE_CHANNEL_ACCESS_TOKEN"]))
)
app.config["LINE_API"] = line_api


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
            _reply(event.reply_token, replies)
            # If they just transitioned to 'active', see if a waiting queue
            # member is now matchable with this fresh user.
            refreshed = db.get_player(user_id)
            if refreshed and refreshed.get("status") == "active":
                matching.try_match_from_queue(line_api, refreshed)
            return
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

    m = re.match(r"^skip_(\d+)$", text)
    if m:
        match_id = int(m.group(1))
        replies, pushes = matching.handle_match_skip(user_id, match_id)
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
    pairs = matching.initiate_matches(player)
    if not pairs:
        db.enqueue_waiting(player["line_user_id"])
        return _reply(reply_token, [TextMessage(text=msg.WAITING_QUEUED)])

    # Reply to caller: summary + one card per candidate (LINE caps at 5 messages).
    cards_for_caller = [matching.build_match_card(c, mid) for c, mid in pairs]
    summary = TextMessage(text=msg.match_parallel_sent(len(pairs)))
    _reply(reply_token, [summary, *cards_for_caller])

    # Push the invite to each candidate.
    for c, mid in pairs:
        line_api.push_message(PushMessageRequest(
            to=c["line_user_id"],
            messages=[matching.build_match_card(player, mid)],
        ))


# --- Entry point -----------------------------------------------

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5001))
    print(f"Tennis Matcher Bot v2 listening on http://localhost:{port}")
    print(f"  webhook: http://localhost:{port}/webhook")
    print(f"  admin:   http://localhost:{port}{admin_base_path()}")
    expiration.start_expiration_thread(line_api)
    app.run(port=port, debug=False)
