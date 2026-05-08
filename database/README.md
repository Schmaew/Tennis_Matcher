# Database — ระบบนำเข้าข้อมูลสนาม

โฟลเดอร์นี้ใช้สำหรับนำเข้าข้อมูลสนามกีฬาจากไฟล์ Excel เข้าสู่ฐานข้อมูล Supabase พร้อมทำ Geocoding โดยอัตโนมัติ

## ไฟล์ในโฟลเดอร์

| ไฟล์                  | หน้าที่                                               |
| --------------------- | ----------------------------------------------------- |
| `TennisMatching.xlsx` | ไฟล์ Excel ต้นฉบับที่รวบรวมข้อมูลสนามทั่วประเทศไทย    |
| `create_table.sql`    | SQL สำหรับสร้างตาราง `courts` ใน Supabase             |
| `import_courts.py`    | สคริปต์หลักสำหรับนำเข้าข้อมูลจาก Excel ไปยัง Supabase |
| `requirements.txt`    | Python dependencies                                   |
| `.env`                | ตัวแปรสภาพแวดล้อม (Supabase credentials)              |

## โครงสร้างตาราง `courts`

```sql
id, province, name_en, name_th, location,
google_maps_url, phone, line_id, facebook,
gmaps_verified_url, stars, reviews, lat, lng, created_at
```

- `(name_en, province)` เป็น UNIQUE key ป้องกันข้อมูลซ้ำ
- มี Index บน `province` และ `lat, lng` เพื่อให้ query เร็ว

## วิธีใช้งาน

### 1. ติดตั้ง Dependencies

```bash
pip install -r requirements.txt
```

### 2. ตั้งค่า .env

```env
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_SERVICE_KEY=eyJ...
```

### 3. สร้างตารางใน Supabase

รันไฟล์ `create_table.sql` ใน Supabase SQL Editor

### 4. รันสคริปต์นำเข้าข้อมูล

```bash
python import_courts.py
```

## การทำงานของ import_courts.py

1. อ่านข้อมูลจาก Excel (sheet: "Research - All Courts")
2. หาพิกัด lat/lng จาก Google Maps URL โดยตรง (เร็วที่สุด)
3. ถ้าไม่มี URL ให้ Geocode ผ่าน Nominatim / OpenStreetMap (ฟรี ไม่ต้องใช้ API Key)
4. Upsert ข้อมูลเข้า Supabase เป็น batch ละ 50 แถว
5. รันซ้ำได้โดยไม่เกิดข้อมูลซ้ำ (idempotent)

## หมายเหตุ

- Nominatim จำกัดที่ 1 request/วินาที สคริปต์จัดการให้อัตโนมัติ
- ถ้า Geocode ไม่สำเร็จ สคริปต์จะลองใช้ query สั้นลงอัตโนมัติสูงสุด 3 ครั้ง
- ไม่ต้องใช้ Google Maps API Key
