# Intensive Lab — LINE Bot Features (90 minutes)

## Purpose

ทำให้ผู้เรียนสามารถเพิ่มฟีเจอร์พื้นฐานให้บอทภายใน 90 นาที: onboarding, คำสั่งสถานะ, และค้นหาเพื่อนตามระดับฝีมือ

## Prerequisites

- `lineofficial-v2` เซิร์ฟเวอร์รันบนเครื่อง และเปิดผ่าน ngrok
- ไฟล์ `.env` ตั้งค่า LINE และ Supabase keys แล้ว
- ติดตั้งตาราง `players` ใน Supabase (จาก `migrations/players.sql`)

## เวลาและโครงสร้าง (90 นาที)

1. 10 min — Quick review & test environment (เชื่อม ngrok, ส่งข้อความทดสอบ)
2. 20 min — Feature A: Onboarding (เก็บ `nickname`)
3. 25 min — Feature B: คำสั่ง `สถานะ` (แสดงข้อมูลผู้เล่น)
4. 25 min — Feature C: คำสั่ง `หาเพื่อน <skill>` (ค้นหาเพื่อนตามระดับ)
5. 10 min — Wrap-up, demo, Q&A

## Deliverables (สิ่งที่ต้องส่ง)

- Patch (diff) ที่แก้ `onboarding.py` และ/หรือ `server.py`
- Transcript หรือ screenshot ของแชทที่แสดงการตอบของบอท
- คำสั่ง SQL ที่รันหรือ screenshot จาก Supabase ที่แสดง row ของ `players`

## Quick Implementation Guide (แบ่งเป็นขั้นตอนชัดเจน)

Feature A — Onboarding: เก็บ `nickname` (20 min)

1. เมื่อผู้ใช้ `follow` บอท: เรียก `db.upsert_player(line_user_id)` (มีใน `server.py` แล้ว)
2. ส่งข้อความถามชื่อเล่น และบันทึกสถานะ onboarding:
   - ข้อความตัวอย่าง: "สวัสดี! ขอบคุณที่เพิ่มบอท 😊 กรุณาพิมพ์ชื่อเล่นของคุณ"
   - ตั้ง `onboarding_step = 1` ในฐานข้อมูล
3. เมื่อรับข้อความจากผู้ใช้และ `onboarding_step == 1`:
   - เรียก `db.update_player(user_id, {'nickname': text, 'onboarding_step': 2})`
   - ตอบกลับ: "ขอบคุณ! ชื่อเล่นถูกบันทึกแล้ว: {nickname}"

Hint (โค้ดสั้นๆ):

```python
player = db.get_player(user_id)
if player and player.get('onboarding_step') == 1:
    db.update_player(user_id, {'nickname': text, 'onboarding_step': 2})
    line_api.reply_message(..., messages=[TextMessage(text=f'ขอบคุณ! ชื่อเล่นถูกบันทึกแล้ว: {text}')])
    return
```

Feature B — คำสั่ง `สถานะ` (25 min)

1. เมื่อข้อความเท่ากับ `สถานะ` ให้ดึงข้อมูลผู้เล่นด้วย `db.get_player(user_id)`
2. ตอบข้อความสั้น ๆ ที่มี `nickname`, `status`, `skill_level` เช่น:
   - "สถานะของคุณ: ชื่อเล่น=Ton | สถานะ=active | ระดับ=casual"

Example:

```python
if text.strip() == 'สถานะ':
    player = db.get_player(user_id)
    if not player:
        reply = 'ไม่พบข้อมูลของคุณ'
    else:
        reply = f"สถานะของคุณ: ชื่อเล่น={player.get('nickname') or '-'} | สถานะ={player.get('status','-')} | ระดับ={player.get('skill_level') or '-'}"
    line_api.reply_message(..., messages=[TextMessage(text=reply)])
    return
```

Feature C — คำสั่ง `หาเพื่อน <skill>` (25 min)

1. ตรวจจับรูปแบบข้อความ `หาเพื่อน <skill>` (รองรับ alias ภาษาไทย/อังกฤษ)
2. เรียก `db.get_active_players()` แล้วกรอง `skill_level == skill` และไม่ใช่ผู้ส่ง
3. ถ้าพบผู้เล่นคนอื่น ให้สร้างแมตช์ `db.create_match(user_id, other_id)` (หรือส่งคำเชิญ)
4. ตอบผู้ขอด้วยข้อความสรุปและปุ่มยืนยันส่งคำเชิญ

Example snippet:

```python
import re
m = re.match(r"หาเพื่อน\s+(.+)", text)
if m:
    skill = m.group(1).strip().lower()
    candidates = [p for p in db.get_active_players() if p.get('skill_level') == skill and p['line_user_id'] != user_id]
    if not candidates:
        reply = 'ยังไม่มีผู้เล่นระดับนี้ในขณะนี้ — ต้องการให้แจ้งเมื่อมีคนใหม่ไหม?'
    else:
        other = candidates[0]
        match_id = db.create_match(user_id, other['line_user_id'])
        reply = f'พบผู้เล่น: {other.get("nickname") or other["line_user_id"]} — สร้างแมตช์ id={match_id} (รอการตอบรับ)'
    line_api.reply_message(..., messages=[TextMessage(text=reply)])
    return
```

## UX Tips (ทำให้แล็ปน่าสนใจ)

- ใช้ข้อความตัวอย่างและ quick-reply buttons: ลดการพิมพ์ของผู้เรียน
- Onboarding แบบเป็นขั้นตอน: ขอทีละข้อมูล (ชื่อเล่น → ระดับ → พื้นที่)
- ยืนยันผลการบันทึกเสมอ เพื่อให้ผู้เรียนเห็น feedback ชัดเจน
- ให้ตัวอย่าง transcript สั้น ๆ เพื่อเป็นตัวชี้วัดว่า "สำเร็จ"

Stretch ideas (ถ้าทันเวลา)

- กรองตาม `area` เพื่อจับคู่ผู้เล่นใกล้เคียง
- เพิ่มหน้า admin แสดงแมตช์ล่าสุด (`admin.py`)
- เขียน unit test เล็ก ๆ สำหรับการ map intent (เช่น alias ของระดับฝีมือ)

## Assessment & Demo (10 min)

แต่ละคนเตรียม 3 สิ่ง:

1. Patch (diff) ของโค้ดที่แก้
2. Screenshot หรือ SQL output ที่แสดง `players` ถูกอัพเดต
3. Transcript ของการโต้ตอบ (onboarding, สถานะ หรือ หาเพื่อน)

---

ถ้าต้องการ ผมจะแปลงตัวอย่างข้อความ prompt ที่เป็นมิตร (quick-replies และตัวเลือกปุ่ม) ให้เป็น patch โค้ดสำหรับ `onboarding.py`/`server.py` ต่อได้เลย
