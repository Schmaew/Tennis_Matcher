Solutions — LINE Bot Workshop
=================================

Task 1 — Intent alias
Add this line into `PROVINCE_ALIASES` inside `intent.py`:

    "korat": "นครราชสีมา",

Save and restart the server. Test with: `tennis korat`.

Task 2 — เพิ่มชนิดกีฬา
If the project uses `SPORT_NAME_KEYWORDS`, add a mapping:

    "pickleball": ["pickleball", "ปิคเกิลบอล"],

Then ensure the filter that checks names uses this key.

Task 3 — ตรวจสอบ `players`
Expected row example in Supabase `players` table:

| line_user_id | status     | onboarding_step | registered_at |
|--------------|------------|-----------------|---------------|
| U1234567890  | onboarding | 0               | 2026-06-05... |

Task 4 — เพิ่มคำสั่ง `สถานะ`
Example snippet to add in `server.py` inside the text handler branch:

```python
from linebot.v3.messaging import TextMessage

if text == "สถานะ":
    player = db.get_player(user_id)
    status = player['status'] if player else 'no record'
    line_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[TextMessage(text=f"สถานะของคุณ: {status}")]
        )
    )
    return
```

Testing
- Restart server and send `สถานะ` to bot. It should reply with current status.
