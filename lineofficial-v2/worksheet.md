LINE Bot Workshop — Worksheet
=================================

สภาพแวดล้อม: เราจะใช้โฟลเดอร์ `lineofficial-v2` (มี `server.py`) ที่รันแล้ว, ngrok ทำงาน และ LINE ตอบกลับได้

เวลาโดยประมาณ: 30–45 นาที (หลังจากเซ็ตอัพเสร็จแล้ว)

วัตถุประสงค์
- เข้าใจการทำงานของ `intent.py`, `db.py` และการส่งข้อความตอบกลับ
- แก้ไขโค้ดเพื่อเพิ่มคำค้นหรือ alias ใหม่
- ตรวจสอบข้อมูลใน Supabase (ตาราง `players` / `matches`)

Task 1 — Intent alias (10 นาที)
1. เปิดไฟล์ `intent.py`
2. เพิ่ม alias ใหม่ให้จังหวัดโคราช: `"korat": "นครราชสีมา"` ใน `PROVINCE_ALIASES`
3. รีสตาร์ทเซิร์ฟเวอร์ และทดสอบด้วยข้อความ `tennis korat`

Checkpoint: Bot เข้าใจ `korat` เป็น `นครราชสีมา` และตอบผลตามจังหวัด

Task 2 — เพิ่มชนิดกีฬา (15 นาที)
1. ถ้าโค้ดมี `SPORT_NAME_KEYWORDS` ให้เพิ่มคีย์สำหรับกีฬาใหม่ เช่น `"pickleball": ["pickleball", "ปิคเกิลบอล"]`
2. รีสตาร์ทเซิร์ฟเวอร์และทดสอบด้วยข้อความตัวอย่าง

Checkpoint: Bot กรองผลลัพธ์ตามคำกีฬาใหม่ได้

Task 3 — ตรวจสอบข้อมูลผู้ใช้ใน Supabase (10 นาที)
1. เข้า Supabase → Table Editor → `players`
2. ให้เพิ่มบอทเป็นเพื่อนและส่งข้อความเริ่มต้น
3. ยืนยันว่าแถวผู้เล่นถูกสร้าง (`line_user_id`, `status`, `onboarding_step`)

Checkpoint: นักเรียนเห็นข้อมูล `players` ถูกสร้างเมื่อเพิ่มบอท

Task 4 — เพิ่มคำสั่ง `สถานะ` (20 นาที)
1. ใน `server.py` หา handler รับข้อความ (`on_text_message`) แล้วเพิ่มกรณีเมื่อตรวจพบคำ `สถานะ` ให้เรียก `db.get_player(user_id)` และส่งข้อความสถานะปัจจุบัน
2. ทดสอบโดยส่ง `สถานะ`

Checkpoint: เมื่อส่ง `สถานะ` บอทตอบสถานะผู้ใช้

Debugging hints
- ถ้า `Verify` ใน LINE Console ขึ้น failed: ตรวจสอบ `ngrok` URL, รีสตาร์ทเซิร์ฟเวอร์, ตรวจสอบ `.env`
- ถ้าเรียก Supabase แล้วฟ้อง 403: ตรวจสอบ `SUPABASE_SERVICE_KEY` ว่าเป็น service_role (secret)

Submission
- ส่งไฟล์ `intent.py` ที่แก้ไขแล้ว (diff) และอธิบายผลลัพธ์สั้น ๆ
