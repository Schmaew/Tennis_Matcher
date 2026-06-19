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
    "ตอบคำถามสั้น ๆ 4 ข้อ แล้วลิงจะหาคู่ตีให้นะครับ 🐵"
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

Q_LINE_BASIC_ID = (
    "LINE ID ของคุณคืออะไรครับ? 📱\n"
    "(ใช้สำหรับให้คู่ตีติดต่อหลังจับคู่สำเร็จ)\n"
    "ตัวอย่าง: @tennis123 หรือ tennis123"
)

Q_LINE_BASIC_ID_INVALID = (
    "LINE ID ไม่ถูกต้องครับ 😅\n"
    "ต้องเป็นตัวอักษรพิมพ์เล็ก/ตัวเลข/จุด/ขีดกลาง/ขีดล่าง ความยาว 4-20 ตัว\n"
    "ลองพิมพ์ใหม่อีกครั้งครับ"
)


def confirm_line_basic_id(basic_id: str) -> str:
    return (
        f"ขอตรวจสอบ LINE ID หน่อยครับ 🔍\n\n"
        f"กดลิงก์นี้ — ถ้าเปิดเป็นโปรไฟล์ของตัวคุณเอง แปลว่า ID ถูกต้อง:\n"
        f"https://line.me/R/ti/p/~{basic_id}\n\n"
        f"ใช่โปรไฟล์ของคุณไหมครับ?"
    )


CONFIRM_YES = "ใช่ ✅"
CONFIRM_NO = "ไม่ใช่ ❌"


# ---------- Status / commands ----------

def player_status(player: dict) -> str:
    skill = SKILL_LABELS.get(player.get("skill_level"), "-")
    basic_id = player.get("line_basic_id")
    line_id_display = f"@{basic_id}" if basic_id else "-"
    return (
        f"📋 ข้อมูลของคุณ\n\n"
        f"ชื่อเล่น: {player.get('nickname') or '-'}\n"
        f"ระดับ: {skill}\n"
        f"โซน: {player.get('area') or '-'}\n"
        f"LINE ID: {line_id_display}\n"
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


def match_introduction(self_nick: str, other_nick: str, other_basic_id: str | None) -> str:
    """Sent to both sides once both accepted. Reveals the other's LINE Basic ID as a tap-to-add link."""
    if other_basic_id:
        link = f"https://line.me/R/ti/p/~{other_basic_id}"
        contact = (
            f"\n\nกดเพิ่มเพื่อนได้เลย 🎾\n{link}"
            f"\n\nถ้ากดไม่ขึ้น ลองค้นด้วย LINE ID: @{other_basic_id}"
        )
    else:
        contact = " 🎾"
    return (
        f"🎉 ทั้งสองฝ่ายตอบรับแล้ว!\n\n"
        f"คุณ {self_nick} เจอกับ {other_nick}"
        f"{contact}"
    )


MATCH_NO_CANDIDATES = (
    "ตอนนี้ยังไม่มีคู่ตีในโซนเดียวกัน 😅\n"
    "ลิงจะแจ้งทันทีที่มีคนสมัครเพิ่ม"
)
MATCH_ACCEPTED_WAIT  = (
    "🐵 รับทราบ! รอดูว่าอีกฝ่ายตอบรับไหมนะครับ\n"
    "(กด ⏭️ ข้าม ถ้าไม่อยากรอคนนี้แล้ว)"
)
MATCH_SKIPPED_ACK = "🐵 ข้ามแล้ว — คนนี้จะเจอน้อยลงในครั้งหน้า"
MATCH_DECLINED       = "🐵 โอเคครับ ไว้หาคู่ใหม่ให้นะ"
MATCH_PARTNER_DECLINED = (
    "😢 อีกฝ่ายไม่สะดวกในครั้งนี้\n"
    "ลองหาคู่ตีคนใหม่ได้เลยครับ"
)
MATCH_EXPIRED = (
    "⏰ ครบกำหนดเวลาแล้ว อีกฝ่ายยังไม่ตอบกลับ\n"
    "ลองหาคู่ตีคนใหม่ได้เลยครับ"
)
MATCH_CANCELED_OTHER = "อีกฝ่ายเจอคู่ตีคนอื่นไปแล้ว 😅"


def match_parallel_sent(n: int) -> str:
    return f"🐵 ส่งคำขอให้ {n} คนแล้ว ใครตอบรับก่อนได้คู่ก่อนนะครับ"


WAITING_QUEUED = (
    "🐵 ยังไม่มีคู่ตีในโซนเดียวกันตอนนี้\n"
    "จัดคุณเข้าคิวให้แล้ว — จะแจ้งทันทีที่มีคู่ตีคนใหม่สมัครเข้ามาในโซนครับ"
)
