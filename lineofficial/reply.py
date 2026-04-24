"""
reply.py
================================================================
Builds LINE message objects from court data.

build_text(text)   -> TextMessage
build_flex(courts) -> dict  (Flex Message carousel container)
================================================================
"""

from linebot.v3.messaging import TextMessage


def build_text(text: str) -> TextMessage:
    return TextMessage(text=text)


def build_flex(courts: list) -> dict:
    """
    Returns a Flex Message carousel container dict with one
    bubble card per court.
    """
    return {
        "type": "carousel",
        "contents": [_court_bubble(c) for c in courts],
    }


def _court_bubble(court: dict) -> dict:
    """
    Builds a single Flex bubble for one court row.
    Shows name, province, location, phone, stars, and map button.
    """
    name     = court.get("name_en") or court.get("name_th") or "Unknown"
    province = court.get("province") or ""
    location = court.get("location") or ""
    phone    = court.get("phone") or ""
    stars    = court.get("stars")
    maps_url = court.get("gmaps_verified_url") or court.get("google_maps_url") or ""

    # Build lat/lng fallback map URL if no stored URL
    if not maps_url and court.get("lat") and court.get("lng"):
        maps_url = (
            f"https://www.google.com/maps/search/?api=1"
            f"&query={court['lat']},{court['lng']}"
        )

    rating_text = f"  {stars}" if stars else "No rating"

    body_contents = [
        {
            "type": "text",
            "text": f"{province}",
            "size": "xs",
            "color": "#888888",
            "margin": "none",
        },
    ]

    if location:
        body_contents.append({
            "type": "text",
            "text": location,
            "size": "xs",
            "color": "#555555",
            "wrap": True,
            "margin": "sm",
        })

    if phone:
        body_contents.append({
            "type": "text",
            "text": f"Tel: {phone}",
            "size": "xs",
            "color": "#555555",
            "margin": "sm",
        })

    body_contents.append({
        "type": "text",
        "text": rating_text,
        "size": "xs",
        "color": "#888888",
        "margin": "sm",
    })

    # Map button (only if URL available)
    footer_contents = []
    if maps_url:
        footer_contents.append({
            "type": "button",
            "style": "primary",
            "color": "#2ECC71",
            "height": "sm",
            "action": {
                "type": "uri",
                "label": "View on Maps",
                "uri": maps_url,
            },
        })

    bubble = {
        "type": "bubble",
        "size": "kilo",
        "header": {
            "type": "box",
            "layout": "vertical",
            "backgroundColor": "#d4edda",
            "paddingAll": "12px",
            "contents": [
                {
                    "type": "text",
                    "text": name,
                    "weight": "bold",
                    "size": "sm",
                    "wrap": True,
                    "color": "#1a1a2e",
                }
            ],
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "contents": body_contents,
        },
    }

    if footer_contents:
        bubble["footer"] = {
            "type": "box",
            "layout": "vertical",
            "contents": footer_contents,
        }

    return bubble
