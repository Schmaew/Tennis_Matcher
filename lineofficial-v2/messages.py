"""
messages.py
================================================================
All user-facing Thai text lives here.

Why centralize?
- One place to fix typos, change tone, swap emojis.
- Easy to add a second language later (just split this file).
- Prevents string-soup in the business logic.

🎓 CUSTOMIZE: edit any string below to change the bot's voice.
================================================================
"""

# Friendly labels mapped from internal codes -> what the user sees.
SKILL_LABELS = {
    "beginner":     "🌱 เริ่มต้น",
    "casual":       "🎾 พอตีได้",
    "intermediate": "💪 เล่นเป็น",
    "competitive":  "🏆 แข่งได้",
}

AREA_OPTIONS = [
    "บางนา / ศรีนครินทร์",
    "สุขุมวิท / ทองหล่อ",
    "รามคำแหง / บางกะปิ",
    "สีลม / สาทร / ลุมพินี",
]


# ---------- Lifecycle ----------

WELCOME = (
    "สวัสดีครับ! 🎾\n\n"
    "ยินดีต้อนรับสู่ Tennis Matcher!\n"
    "ตอบคำถามสั้น ๆ 3 ข้อ แล้วลิงจะหาคู่ตีให้นะครับ 🐵"
)

ONBOARDING_DONE = (
    "ลงทะเบียนเรียบร้อย! 🎉\n\n"
    "พิมพ์ 'หาคู่' เพื่อหาคู่ตีในโซนเดียวกัน\n"
    "พิมพ์ 'สถานะ' ดูข้อมูล\n"
    "พิมพ์ 'หยุด' / 'เริ่ม' หยุดพักหรือกลับมา\n"
    "พิมพ์ 'ลิงรีเซ็ต' ลบข้อมูลแล้วเริ่มใหม่ (สำหรับทดสอบ)"
)


# ---------- Onboarding questions ----------

Q_NICKNAME = "ชื่อเล่นที่อยากให้เรียกครับ?"

Q_SKILL = "เล่นเทนนิสระดับไหนครับ? 🎾"

Q_AREA = "สะดวกเล่นแถวไหนครับ? 📍"


# ---------- Status / commands ----------

def player_status(player: dict) -> str:
    skill = SKILL_LABELS.get(player.get("skill_level"), "-")
    return (
        f"📋 ข้อมูลของคุณ\n\n"
        f"ชื่อเล่น: {player.get('nickname') or '-'}\n"
        f"ระดับ: {skill}\n"
        f"โซน: {player.get('area') or '-'}\n"
        f"สถานะ: {player.get('status')}"
    )


PAUSED = "⏸️ หยุดรับคู่ตีชั่วคราว พิมพ์ 'เริ่ม' เมื่อพร้อม"
RESUMED = "✅ กลับมาแล้ว! พิมพ์ 'หาคู่' เมื่ออยากตีนะครับ"
RESET_DONE = "🐵 ลบข้อมูลแล้ว มาเริ่มใหม่กันครับ"

UNKNOWN = (
    "🐵 พิมพ์ 'หาคู่' หาคู่ตี | 'สถานะ' ดูข้อมูล | "
    "'หยุด'/'เริ่ม' พัก/กลับมา"
)


# ---------- Matching ----------

def match_invite(other: dict) -> str:
    """Sent to both sides when a match is suggested."""
    skill = SKILL_LABELS.get(other.get("skill_level"), "-")
    return (
        f"🎾 เจอคู่ตีให้แล้ว!\n\n"
        f"ชื่อเล่น: {other.get('nickname')}\n"
        f"ระดับ: {skill}\n"
        f"โซน: {other.get('area')}\n\n"
        f"สนใจตีด้วยกันไหมครับ?"
    )


def match_introduction(self_nick: str, other_nick: str, other_user_id: str) -> str:
    """Sent to both sides once both accepted. Reveals the other's LINE user id."""
    return (
        f"🎉 ทั้งสองฝ่ายตอบรับแล้ว!\n\n"
        f"คุณ {self_nick} เจอกับ {other_nick}\n"
        f"LINE ID อีกฝ่าย: {other_user_id}\n\n"
        f"ลองทักไปนัดวันตีกันได้เลย 🎾"
    )


MATCH_NO_CANDIDATES = (
    "ตอนนี้ยังไม่มีคู่ตีในโซนเดียวกัน 😅\n"
    "ลิงจะแจ้งทันทีที่มีคนสมัครเพิ่ม"
)
MATCH_ACCEPTED_WAIT  = "🐵 รับทราบ! รอดูว่าอีกฝ่ายตอบรับไหมนะครับ"
MATCH_DECLINED       = "🐵 โอเคครับ ไว้หาคู่ใหม่ให้นะ"
