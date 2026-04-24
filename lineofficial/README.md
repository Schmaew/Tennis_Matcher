1. ติดตั้ง
bashpip install pandas openpyxl supabase httpx python-dotenv
pip install -r requirements.txt

2. ตั้งค่า .env
bashcp .env.example .env
# แก้ใส่ keys จริง

3. หา LINE keys — ไปที่ developers.line.biz → channel → tab Messaging API

Channel secret
กด Issue → Channel access token

4. รัน server
bashpython server.py

5. Expose ด้วย ngrok (terminal ใหม่)
bashngrok http 5000
จะได้ URL เช่น https://abc123.ngrok.io

6. ใส่ webhook URL ใน LINE Console
https://abc123.ngrok.io/webhook
Messaging API tab → Webhook URL → Verify → ต้องขึ้น Success

Pattern ที่รู้จักแล้ว
ข้อความผลลัพธ์สนามแบดมินตันพิจิตรbadminton courts in พิจิตรtennis court Bangkoktennis courts in กรุงเทพคอร์ตเทนนิสเชียงใหม่tennis courts in เชียงใหม่badminton Khon Kaenbadminton courts in ขอนแก่นสวัสดี / hellowelcome messagehelp / ช่วยusage instructions