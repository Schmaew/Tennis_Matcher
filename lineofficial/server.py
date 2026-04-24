"""
server.py
================================================================
LINE Messaging API webhook server.

Receives messages from LINE, detects intent (sport + province),
queries courts from Supabase, and replies with a Flex Message.

Setup:
    1. pip install flask line-bot-sdk supabase python-dotenv
    2. Copy .env.example to .env and fill in your keys.
    3. python server.py
    4. Expose port 5000 via ngrok: ngrok http 5000
    5. Paste the ngrok URL into LINE Developers console as webhook URL.

.env variables required:
    LINE_CHANNEL_SECRET=...
    LINE_CHANNEL_ACCESS_TOKEN=...
    SUPABASE_URL=...
    SUPABASE_SERVICE_KEY=...
================================================================
"""

import os
from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
    FlexMessage,
    FlexContainer,
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from supabase import create_client
from dotenv import load_dotenv

from intent import detect_intent
from reply import build_flex, build_text

load_dotenv()

# -- Clients --------------------------------------------------
app = Flask(__name__)

handler = WebhookHandler(os.environ["LINE_CHANNEL_SECRET"])

line_api = MessagingApi(
    ApiClient(Configuration(access_token=os.environ["LINE_CHANNEL_ACCESS_TOKEN"]))
)

sb = create_client(
    os.environ["SUPABASE_URL"],
    os.environ["SUPABASE_SERVICE_KEY"],
)


# -- Webhook endpoint -----------------------------------------
@app.route("/webhook", methods=["POST"])
def webhook():
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"


# -- Message handler ------------------------------------------
@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_text = event.message.text.strip()
    intent = detect_intent(user_text)

    if intent["type"] == "find_court":
        courts = query_courts(intent["province"], intent["sport"])
        if courts:
            sport_label = intent["sport"] or "court"
            province_label = intent["province"] or "nearby"
            messages = [
                TextMessage(
                    text=f"Found {len(courts)} {sport_label} court(s) in {province_label}:"
                ),
                FlexMessage(
                    alt_text=f"{sport_label} courts in {province_label}",
                    contents=FlexContainer.from_dict(build_flex(courts)),
                ),
            ]
        else:
            messages = [build_text("No courts found for that location. Try a different province or sport.")]

    elif intent["type"] == "greeting":
        messages = [build_text(
            "Hello! I can help you find tennis and badminton courts.\n\n"
            "Try:\n"
            "- 'badminton court in Phichit'\n"
            "- 'tennis court Bangkok'\n"
            "- 'สนามแบดมินตันพิจิตร'"
        )]

    elif intent["type"] == "help":
        messages = [build_text(
            "How to use:\n\n"
            "Type a sport + province, for example:\n"
            "- 'tennis court Chiang Mai'\n"
            "- 'badminton Khon Kaen'\n"
            "- 'สนามเทนนิสกรุงเทพ'"
        )]

    else:
        messages = [build_text(
            "I did not understand that. Try typing a sport and province, "
            "e.g. 'tennis court Bangkok'."
        )]

    line_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=messages,
        )
    )


# -- Supabase query -------------------------------------------
def query_courts(province: str | None, sport: str | None) -> list:
    """
    Returns up to 5 courts filtered by province and/or sport.
    Falls back gracefully if either filter is absent.
    """
    q = sb.table("courts").select(
        "name_en, name_th, province, location, phone, "
        "line_id, google_maps_url, gmaps_verified_url, stars, lat, lng"
    )

    if province:
        q = q.ilike("province", f"%{province}%")

    if sport:
        q = q.in_("sport_type", [sport, "multi"])

    result = q.order("stars", desc=True).limit(5).execute()
    return result.data or []


# -- Entry point ----------------------------------------------
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print(f"Server running on port {port}")
    print("Expose with: ngrok http {port}")
    app.run(port=port, debug=False)
