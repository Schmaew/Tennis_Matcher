# Tennis Monkey example → Student teaching plan

## What the senior's repo is
A production-grade LINE OA bot, ~thousands of lines:

| Layer | Technology |
|---|---|
| Runtime | **Node.js** (no framework — raw `http` server) |
| Database | **Postgres** (5 schema migrations: v1→v5) |
| LINE SDK | `@line/bot-sdk` v11 (Node, not Python) |
| Image storage | **Google Cloud Storage** (coach profile photos) |
| Cron scripts | Standalone Node files (weekly matching, daily outcome ping) |
| Admin dashboard | HTML + JS dashboard at `/api/admin` (funnel, players, coaches, matches, boosts) |
| Security | CSP, rate limiting, signature verify, 1MB body cap, image magic-byte check, opaque GCS paths, parametrized SQL with column whitelist |

## Key architectural patterns worth teaching
1. **State machine onboarding** — `players.onboarding_step` 0→7, each step asks one question, each reply advances the state. Same pattern for coaches.
2. **Two-sided marketplace** — players AND coaches register, system matches them.
3. **Quick-reply tokens** — bot sends `accept_<id>`, user taps button, bot dispatches via regex on `text`.
4. **Public IDs vs LINE user IDs** — `coach_num` (integer) used in chat tokens, never expose `line_user_id`.
5. **Weekly matching cron** — separate script (`scripts/run-matching.js`) ranks player pairs and pushes notifications.
6. **Admin dashboard analytics** — funnel: registered → onboarded → showed interest → introduced → attended.
7. **Boost SKU** — paid feature that bumps coaches in search results. Manual activation via PromptPay slip → admin click.

## Honest scope check

**Cloning this would be days of work** and it's a big jump for a beginner:
- New language: student is on Python/Flask; example is Node.js
- New database: student is on Supabase REST; example uses raw SQL via `pg` pool
- New domain primitive: state-machine onboarding, marketplace logic
- ~10 new src files, 5 SQL migrations, GCS account setup

The student's current `lineofficial/server.py` is ~150 lines doing one thing (court search). The leap is enormous.

## Three realistic options

### Option A — Teach FROM the senior's repo (no rebuild)
Use the senior's repo as the textbook. Set up an annotated walkthrough document mapping each concept (state machine, quick-reply tokens, admin dashboard) to specific files + lines. Give the student concrete "find and modify" exercises in the senior's code (rename brand, change onboarding questions, add a new command).
- ✅ Fastest. Zero duplicate code to maintain.
- ✅ Student learns to read production code (a real skill).
- ❌ Student doesn't get the experience of building it themselves.

### Option B — Build a Python "teaching skeleton" (subset)
Keep the student's existing Python/Flask/Supabase stack. Add ONE concept at a time on top of the existing court-search bot:
- Lesson 1: Add a `players` table + `follow` event handler that registers users
- Lesson 2: Add a 3-question onboarding state machine in Python
- Lesson 3: Add quick-reply buttons + token routing
- Lesson 4: Add a simple admin web page to list registered players
- Lesson 5: Add a matching command
- ✅ Stays in familiar stack. Builds incrementally. Student writes every line.
- ❌ Won't match the senior's repo file-for-file.

### Option C — Full Node.js port mirroring the senior's structure
Replace `lineofficial/` with a Node.js bot that mirrors the senior's file layout, but with a smaller feature set the student can grow into.
- ✅ Same shape as the example, easier to "graduate" to it.
- ❌ Stack switch mid-course. Throws away the working Python bot.
- ❌ Most work to set up.

---

## Files I read in the senior's repo
- `README.md`, `package.json`, `server.js`
- `api/webhook.js`
- `src/handlers.js`, `src/db.js`
- `src/onboarding.js` (first 80 lines)
- `src/messages.js` (first 60 lines)
- `db/migration.sql` (v1)
- `tennis-monkey-spec.md` (first 80 lines)

I have NOT yet read: `coach-onboarding.js`, `matching.js`, `coach-search.js`, `line-client.js`, `line-blob.js`, `storage.js`, `admin-auth.js`, the 8 admin endpoints, migrations v2-v5, the cron scripts, or the v2 spec. I can read more if you pick an option that needs deeper understanding.

## Plan — Option B: Python teaching skeleton, same repo, same domain

**Where it lives:** new folder `lineofficial-v2/` next to existing `lineofficial/`. Original court-search bot stays working — student can run both, diff them, see the evolution.

**Stack:** Python + Flask + Supabase (matches existing student knowledge). NO Node.js. NO new infrastructure.

### The 5-lesson arc (mirrors senior's concepts)

Each lesson adds ONE concept on top of the previous. Each lesson = one file change OR one small new file. Student writes every line; teacher walks through.

| # | Lesson | What student adds | Maps to senior's repo |
|---|---|---|---|
| 1 | **User registration + `follow` event** | New `players` table in Supabase; handle `follow` event → create row + welcome message; `สถานะ` command shows profile | `db/migration.sql` `players` table + `handlers.js` follow event |
| 2 | **3-question onboarding state machine** | `onboarding_step` column drives dispatch; questions: nickname → skill → area | `src/onboarding.js` |
| 3 | **Quick-reply buttons + token routing** | Bot sends inline buttons; webhook regex-matches `cmd_value` tokens before plain text; `หยุด`/`เริ่ม` pause toggle | `quickReply` + `accept_<id>` token pattern in `handlers.js` |
| 4 | **Simple admin web page** | Flask `/admin` route with Bearer token auth; HTML table of all players | `api/admin/players.js` + `admin-auth.js` |
| 5 | **Player ↔ player matching command** | `หาคู่` → finds another active player same area + similar skill → sends each side the other's contact | `src/matching.js` (drastically simplified) |

### What I will deliver (assuming you say "go" to building all 5)

| File | Purpose |
|---|---|
| `lineofficial-v2/server.py` | Flask app, webhook signature verification, route dispatch — copies the structure of existing `lineofficial/server.py` and grows |
| `lineofficial-v2/db.py` | Supabase queries: `get_player`, `upsert_player`, `update_player`, `get_active_players` |
| `lineofficial-v2/onboarding.py` | State machine — `start_onboarding`, `handle_onboarding_message` |
| `lineofficial-v2/messages.py` | Thai message strings (centralized like senior's `messages.js`) |
| `lineofficial-v2/quick_reply.py` | Helper to build LINE quick-reply payloads + token regex matching |
| `lineofficial-v2/matching.py` | Player matching algorithm (lesson 5) |
| `lineofficial-v2/admin.py` | Flask blueprint for `/admin` page (lesson 4) |
| `lineofficial-v2/migrations/players.sql` | `players` table schema |
| `lineofficial-v2/.env.example` | Env vars template (LINE keys, Supabase, ADMIN_TOKEN) |
| `lineofficial-v2/requirements.txt` | flask, line-bot-sdk, supabase, python-dotenv |
| `lineofficial-v2/README.md` | How to run + checklist for each lesson |
| `TEACHING_PLAN_V2.md` (root) | Lesson-by-lesson teaching guide with: (a) which senior repo files to show side-by-side, (b) concept explanation in plain language, (c) code template for the student to fill in, (d) "challenge" extensions, (e) marked **CUSTOMIZE HERE** comments in the code so student knows what to change |

### "Where to customize" markers
Inside each Python file I'll put `# 🎓 CUSTOMIZE: <what>` comments at the spots students should edit. Examples:
- `messages.py` → `# 🎓 CUSTOMIZE: change brand voice / emoji here`
- `onboarding.py` → `# 🎓 CUSTOMIZE: add or remove onboarding questions here`
- `matching.py` → `# 🎓 CUSTOMIZE: tune matching weights (skill vs area) here`

These act as the "here's where to make it your own" markers.

### Simplicity constraints I will follow (per project CLAUDE.md)
- One file = one job. No frameworks beyond Flask + supabase-py.
- No SQLAlchemy, no FastAPI, no async — match the existing `lineofficial/server.py` style.
- No fancy testing infra.
- Comments only where the WHY isn't obvious — the `🎓 CUSTOMIZE` markers are the exception (they're a teaching tool).
- Leverage what exists: reuse env loading, signature verification, intent.py keywords as model.

---

## Open scope question

Build all 5 lessons in one go, or start with just Lesson 1 (registration + follow event) and let the student pace through 2-5 over time?

## Review

### What was built

A complete Python teaching skeleton at `lineofficial-v2/` plus a 5-lesson teaching guide at the repo root.

| File | Lines | Purpose |
|---|---|---|
| `lineofficial-v2/server.py` | ~150 | Flask app — webhook entry, follow event, message dispatch, command routing |
| `lineofficial-v2/onboarding.py` | ~120 | 3-step state machine (nickname → skill → area) |
| `lineofficial-v2/matching.py` | ~130 | Score-based partner finding + accept/decline flow |
| `lineofficial-v2/db.py` | ~110 | All Supabase queries with column whitelist |
| `lineofficial-v2/messages.py` | ~100 | All Thai message templates centralized |
| `lineofficial-v2/admin.py` | ~110 | `/admin` HTML + JSON endpoint with Bearer auth |
| `lineofficial-v2/quick_reply.py` | ~50 | LINE quick-reply helper |
| `lineofficial-v2/migrations/players.sql` | ~30 | `players` + `matches` tables |
| `lineofficial-v2/.env.example` | ~25 | Env var template |
| `lineofficial-v2/requirements.txt` | 4 | flask, line-bot-sdk, supabase, python-dotenv |
| `lineofficial-v2/README.md` | ~110 | Setup, file map, run instructions |
| `TEACHING_PLAN_V2.md` (root) | ~270 | 5-lesson guide mapping each concept to senior's repo |

**Total: 12 new files. ~800 lines of code + ~380 lines of docs.**

### What was NOT touched
- `lineofficial/` (original Python bot) — left alone, still works
- `tennis_monkey-main/` (senior's repo) — read-only reference
- All Expo / React Native code

### Verification
- All 7 Python files compile (`python -m py_compile`) — no syntax errors
- Folder structure mirrors senior's logical separation
- Each file has a `🎓 CUSTOMIZE:` marker at every spot the student is meant to edit

### Mapping (concept → senior file → our file)
Documented exhaustively in `TEACHING_PLAN_V2.md` "Why a Python skeleton when the senior wrote Node.js?" section. Highlights:
- Webhook signature verification, top-level event dispatch, state machine, message templates, quick-reply tokens, matching score, Bearer-token admin auth, admin path obfuscation, reset/wipe command, SQL injection defense.

### What was deliberately omitted (and noted in the plan)
- Coaches table + 8-step coach onboarding
- Photo uploads to Google Cloud Storage
- Coach waitlist + auto-notify
- Boost SKU + payment flow
- Daily outcome ping cron
- CSP / rate limiting / body size cap (Flask defaults less strict than the senior's raw Node http server — acceptable for a teaching tool)

### Next steps for the user
1. Open `lineofficial-v2/README.md` → follow Setup steps 1-4 to run it locally
2. Read `TEACHING_PLAN_V2.md` end-to-end to plan the lessons
3. When ready to teach, walk the student through Lesson 1 first
4. Decide whether to commit + push (per your earlier choice, code is uncommitted for review)

### Simplicity check
- No new abstractions beyond what existed in `lineofficial/` (still flask + supabase-py + python-dotenv + line-bot-sdk)
- Each file has one job
- Code style matches existing `lineofficial/server.py` (snake_case, doc comments at top, no class hierarchies)
- No tests, no CI, no Docker — keeps the surface area small for a teaching context
- Comments are sparse except for the `🎓 CUSTOMIZE:` markers (which are intentional teaching tools, not normal code comments)
