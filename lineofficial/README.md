# LINE Official — บอทค้นหาสนามกีฬา

โฟลเดอร์นี้ใช้สำหรับรัน LINE Messaging API Bot ที่รับข้อความจากผู้ใช้และตอบกลับด้วยข้อมูลสนามกีฬาจากฐานข้อมูล Supabase

## ไฟล์ในโฟลเดอร์

| ไฟล์ | หน้าที่ |
|------|---------|
| `server.py` | Flask webhook server รับข้อความจาก LINE |
| `intent.py` | ตรวจจับ intent จากข้อความ (ชนิดกีฬา, จังหวัด) |
| `reply.py` | สร้าง Flex Message สำหรับตอบกลับ |
| `requirements.txt` | Python dependencies |
| `.env` | ตัวแปรสภาพแวดล้อม (LINE keys + Supabase credentials) |

## วิธีติดตั้งและใช้งาน

### 1. ติดตั้ง Dependencies

```bash
pip install -r requirements.txt
```

### 2. ตั้งค่า .env

```env
LINE_CHANNEL_SECRET=xxxx
LINE_CHANNEL_ACCESS_TOKEN=xxxx
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_SERVICE_KEY=eyJ...
```

### 3. หา LINE Keys

ไปที่ [developers.line.biz](https://developers.line.biz) → เลือก Channel → แท็บ **Messaging API**

- **Channel secret** — แสดงในหน้า Basic settings
- **Channel access token** — กด **Issue** ในแท็บ Messaging API

### 4. รัน Server

```bash
python server.py
```

Server จะรันที่ `http://localhost:5000`

### 5. Expose ด้วย ngrok (เปิด terminal ใหม่)

```bash
ngrok http 5000
```

จะได้ URL เช่น `https://abc123.ngrok.io`

### 6. ตั้งค่า Webhook URL ใน LINE Console

ใส่ URL นี้ในช่อง Webhook URL:

```
https://abc123.ngrok.io/webhook
```

Messaging API tab → Webhook URL → **Verify** → ต้องขึ้น **Success**

## รูปแบบข้อความที่รู้จัก

| ข้อความที่ส่ง | ผลลัพธ์ |
|--------------|---------|
| `สนามแบดมินตันพิจิตร` | สนาม Badminton ใน พิจิตร |
| `tennis court Bangkok` | สนาม Tennis ใน กรุงเทพ |
| `คอร์ตเทนนิสเชียงใหม่` | สนาม Tennis ใน เชียงใหม่ |
| `badminton Khon Kaen` | สนาม Badminton ใน ขอนแก่น |
| `สวัสดี` / `hello` | ข้อความต้อนรับ |
| `help` / `ช่วย` | คำแนะนำการใช้งาน |

## การทำงานของบอท

1. ผู้ใช้ส่งข้อความมาที่ LINE
2. `intent.py` วิเคราะห์ข้อความหาชนิดกีฬาและจังหวัด
3. Query ข้อมูลสนามจาก Supabase
4. `reply.py` สร้าง Flex Message (Carousel) ส่งกลับผู้ใช้
