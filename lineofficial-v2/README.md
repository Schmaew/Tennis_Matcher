# lineofficial-v2 — Tennis Matcher Bot (Teaching Skeleton)

A simplified Python LINE bot inspired by the senior's Node.js "Tennis Monkey" repo. Built as a teaching tool: every concept the senior uses appears here in a smaller, easier-to-read form.

**Stack:** Python 3.11+ · Flask · `line-bot-sdk` v3 · Supabase · python-dotenv

---

## Files at a glance

| File | What it does | Lines |
|---|---|---|
| `server.py` | Flask app: webhook entry, event dispatch | ~150 |
| `onboarding.py` | 3-step state machine (nickname → skill → area) | ~120 |
| `matching.py` | Find best partner + handle accept/decline | ~130 |
| `db.py` | All Supabase queries | ~110 |
| `messages.py` | All Thai user-facing strings | ~100 |
| `quick_reply.py` | Helper to build LINE quick-reply buttons | ~50 |
| `admin.py` | `/admin` dashboard with Bearer-token auth | ~110 |
| `migrations/players.sql` | DB schema (players + matches tables) | ~30 |

Total: ~800 lines of Python. Compare to the senior's ~3,000+ lines of Node.js.

---

## Setup

### 1. Install Python deps

```bash
cd lineofficial-v2
pip install -r requirements.txt
```

### 2. Create the database tables

Open Supabase → SQL Editor → paste the contents of [migrations/players.sql](migrations/players.sql) → Run.

You should now have two new tables: `players` and `matches`.

### 3. Configure environment

```bash
cp .env.example .env
```

Edit `.env`:
- `LINE_CHANNEL_SECRET`, `LINE_CHANNEL_ACCESS_TOKEN` — same channel as `lineofficial/`, OR a brand-new channel for testing
- `SUPABASE_URL`, `SUPABASE_SERVICE_KEY` — same Supabase project as `lineofficial/`
- `ADMIN_TOKEN` — generate with `python -c "import secrets; print(secrets.token_hex(16))"`
- `ADMIN_PATH_SECRET` — optional; if set, admin moves from `/admin` to `/<secret>/admin`
- `PORT` — defaults to `5001` (so it doesn't collide with the original bot on `5000`)

### 4. Run

```bash
python server.py
```

Output:
```
Tennis Matcher Bot v2 listening on http://localhost:5001
  webhook: http://localhost:5001/webhook
  admin:   http://localhost:5001/admin
```

### 5. Expose with ngrok and point LINE at it

```bash
ngrok http 5001
```

Paste the `https://xxxxx.ngrok-free.dev/webhook` into LINE Developers Console → Messaging API → Webhook URL → **Verify**. Toggle **Use webhook** ON. Toggle **Auto-reply messages** OFF.

---

## Try it on LINE

1. Add the bot as friend on your phone — it sends a welcome and asks your nickname
2. Type your nickname → it asks your skill (4 buttons)
3. Tap a skill → it asks your area (4 buttons)
4. Tap an area → registration done
5. Type `หาคู่` → if another active player is in your area at a similar skill, you both get a card with `accept` / `decline` buttons. Both accept → both sides get the other's LINE user_id.
6. Type `สถานะ` to view your profile
7. Type `หยุด` / `เริ่ม` to pause/resume
8. Type `ลิงรีเซ็ต` to wipe your row and start onboarding again (great for testing)

## Admin dashboard

Open http://localhost:5001/admin (or http://localhost:5001/&lt;ADMIN_PATH_SECRET&gt;/admin if set). Paste `ADMIN_TOKEN` → see all registered players.

---

## Where to customize

Search the codebase for `🎓 CUSTOMIZE` — every spot the student is meant to edit is marked.

| Location | What you can change |
|---|---|
| `messages.py` (top) | Brand voice, emojis, Thai wording |
| `messages.py` `AREA_OPTIONS` | List of selectable areas |
| `onboarding.py` `_STEP_HANDLERS` | Add or remove onboarding questions |
| `matching.py` `_score()` | Tune match weights (area vs skill) |
| `server.py` `on_text_message` | Add new chat commands |

---

## See also
- [`../TEACHING_PLAN_V2.md`](../TEACHING_PLAN_V2.md) — lesson-by-lesson teaching guide
- [`../tennis_monkey-main/`](../tennis_monkey-main/) — the senior's full reference implementation
- [`../lineofficial/`](../lineofficial/) — the previous (simpler) Python bot
