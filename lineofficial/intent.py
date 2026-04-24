"""
intent.py
================================================================
Parses a raw LINE message into a structured intent dict.

Returns:
    {
        "type":     "find_court" | "greeting" | "help" | "unknown",
        "sport":    "tennis" | "badminton" | "squash" | None,
        "province": "<province name in Thai>" | None,
    }
================================================================
"""

import re

# -- Province list (Thai names, 77 provinces) -----------------
PROVINCES = [
    "กรุงเทพ", "กรุงเทพมหานคร", "กระบี่", "กาญจนบุรี", "กาฬสินธุ์",
    "กำแพงเพชร", "ขอนแก่น", "จันทบุรี", "ฉะเชิงเทรา", "ชลบุรี",
    "ชัยนาท", "ชัยภูมิ", "ชุมพร", "เชียงราย", "เชียงใหม่",
    "ตรัง", "ตราด", "ตาก", "นครนายก", "นครปฐม",
    "นครพนม", "นครราชสีมา", "นครศรีธรรมราช", "นครสวรรค์",
    "นนทบุรี", "นราธิวาส", "น่าน", "บึงกาฬ", "บุรีรัมย์",
    "ปทุมธานี", "ประจวบคีรีขันธ์", "ปราจีนบุรี", "ปัตตานี",
    "พระนครศรีอยุธยา", "พะเยา", "พังงา", "พัทลุง", "พิจิตร",
    "พิษณุโลก", "เพชรบุรี", "เพชรบูรณ์", "แพร่", "ภูเก็ต",
    "มหาสารคาม", "มุกดาหาร", "แม่ฮ่องสอน", "ยโสธร", "ยะลา",
    "ร้อยเอ็ด", "ระนอง", "ระยอง", "ราชบุรี", "ลพบุรี",
    "ลำปาง", "ลำพูน", "เลย", "ศรีสะเกษ", "สกลนคร",
    "สงขลา", "สตูล", "สมุทรปราการ", "สมุทรสงคราม", "สมุทรสาคร",
    "สระแก้ว", "สระบุรี", "สิงห์บุรี", "สุโขทัย", "สุพรรณบุรี",
    "สุราษฎร์ธานี", "สุรินทร์", "หนองคาย", "หนองบัวลำภู",
    "อ่างทอง", "อำนาจเจริญ", "อุดรธานี", "อุตรดิตถ์",
    "อุทัยธานี", "อุบลราชธานี",
]

# Common shorthand / alias -> canonical Thai province name
PROVINCE_ALIASES = {
    "กทม":      "กรุงเทพ",
    "กรุงเทพฯ": "กรุงเทพ",
    "bangkok":  "กรุงเทพ",
    "bkk":      "กรุงเทพ",
    "โคราช":    "นครราชสีมา",
    "korat":    "นครราชสีมา",
    "อยุธยา":   "พระนครศรีอยุธยา",
    "ayutthaya":"พระนครศรีอยุธยา",
    "phuket":   "ภูเก็ต",
    "chiangmai":"เชียงใหม่",
    "chiang mai":"เชียงใหม่",
    "phichit":  "พิจิตร",
    "พิจิตร":   "พิจิตร",
    "khonkaen": "ขอนแก่น",
    "khon kaen":"ขอนแก่น",
    "pattaya":  "ชลบุรี",
}

# Keywords that indicate each sport
SPORT_KEYWORDS = {
    "badminton": [
        "แบดมินตัน", "แบด", "badminton", "ขนไก่", "คอร์ตแบด",
    ],
    "tennis": [
        "เทนนิส", "tennis", "คอร์ตเทนนิส", "สนามเทนนิส",
    ],
    "squash": [
        "สควอช", "squash",
    ],
}

# Patterns that signal a court-search intent
FIND_COURT_PATTERNS = [
    r"สนาม", r"คอร์ต", r"court", r"ที่เล่น", r"หา", r"ใกล้",
    r"มีที่ไหน", r"แนะนำ", r"find", r"where",
]

GREETING_PATTERNS = [r"^สวัสดี", r"^หวัดดี", r"^hello$", r"^hi$", r"^ดี"]
HELP_PATTERNS     = [r"ช่วย", r"help", r"menu", r"เมนู", r"ทำอะไรได้"]


def detect_intent(text: str) -> dict:
    """
    Parses user message and returns a structured intent dict.
    """
    lower = text.lower().strip()

    province = _extract_province(text)
    sport    = _extract_sport(lower)

    # Greeting check
    if any(re.search(p, lower) for p in GREETING_PATTERNS):
        return {"type": "greeting", "sport": None, "province": None}

    # Help check
    if any(re.search(p, lower) for p in HELP_PATTERNS):
        return {"type": "help", "sport": None, "province": None}

    # Court search: explicit pattern OR sport/province detected
    has_find_pattern = any(re.search(p, lower) for p in FIND_COURT_PATTERNS)
    if has_find_pattern or sport or province:
        return {"type": "find_court", "sport": sport, "province": province}

    return {"type": "unknown", "sport": None, "province": None}


def _extract_province(text: str) -> str | None:
    lower = text.lower()

    # Check aliases first (includes English names)
    for alias, canonical in PROVINCE_ALIASES.items():
        if alias in lower or alias in text:
            return canonical

    # Check full Thai province names
    for province in PROVINCES:
        if province in text:
            return province

    return None


def _extract_sport(lower: str) -> str | None:
    for sport, keywords in SPORT_KEYWORDS.items():
        if any(kw.lower() in lower for kw in keywords):
            return sport
    return None
