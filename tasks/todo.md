# Tennis Matcher — Wire Expo App to Supabase + Confirm LINE Bot

## Goal
1. Expo app reads tennis courts from **Supabase** (the imported Thailand data) instead of Google Places.
2. LINE bot answers Thai/English court questions using the same Supabase data — fix existing bug.

---

## Part A — Wire Expo App to Supabase

### A1. Install Supabase client
- [ ] `npm install @supabase/supabase-js`

### A2. Add Supabase env variables
- [ ] Update `.env.example` to document `EXPO_PUBLIC_SUPABASE_URL` and `EXPO_PUBLIC_SUPABASE_ANON_KEY`
- [ ] User creates root `.env` with real values (use **anon key**, never the service key — anon key is safe to bundle in the mobile app)

### A3. Create a tiny Supabase client
- [ ] New file: `services/supabaseClient.ts` — single shared `createClient()` instance

### A4. Create a Supabase courts service
- [ ] New file: `services/courtsSupabaseService.ts`
  - One function: `fetchCourtsFromSupabase()` → `Court[]`
  - Queries `courts` table, orders by `stars DESC`, limit 100
  - Maps DB row → `Court` interface (handles nullable fields with sensible defaults: empty arrays, fallback photo)

### A5. Update `useCourts` hook
- [ ] Replace Google Places call with Supabase call
- [ ] Drop `expo-location` permission flow (no longer needed — we show all Thailand courts)
- [ ] Keep mock fallback if Supabase env is missing or query fails (graceful degradation)

### A6. Test
- [ ] User runs `npx expo start --clear` and opens the Courts tab
- [ ] Verifies real Thai court names show up

---

## Part B — Fix LINE Bot Bug & Confirm Connection

### B1. Fix the `sport_type` bug
**Problem:** `server.py:143` calls `q.in_("sport_type", ...)` but column doesn't exist.

**Simplest fix (least code change):**
- [ ] In `lineofficial/server.py`, replace the `sport_type` SQL filter with a Python-side keyword filter on `name_en` / `name_th` (e.g. if sport=`tennis`, keep rows whose name contains "tennis" / "เทนนิส"). Falls back to all rows if no match.

This avoids changing the schema or re-importing data. Single function change, low risk.

### B2. Verify LINE → Supabase wiring works
- [ ] Confirm `lineofficial/.env` has `LINE_CHANNEL_SECRET`, `LINE_CHANNEL_ACCESS_TOKEN`, `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`
- [ ] Confirm `database/import_courts.py` has been run (Supabase `courts` table is populated)

### B3. Tell user what's needed to go live with the LINE bot
List in the review section — see below.

---

## Simplicity rules I will follow
- No new abstractions; just one client file + one service file mirroring the existing Google Places pattern.
- No backwards-compatibility code — Google Places service stays as-is (won't delete, in case student wants to revisit) but `useCourts` will no longer call it.
- No location permission code path in `useCourts` (Supabase doesn't need GPS).
- LINE bot fix is one function edit, no schema migration.

---

## Files I will touch
| Action | File |
|---|---|
| Create | `services/supabaseClient.ts` |
| Create | `services/courtsSupabaseService.ts` |
| Edit   | `hooks/useCourts.ts` |
| Edit   | `lineofficial/server.py` (`query_courts` function only) |
| Edit   | `.env.example` (add Supabase vars) |
| Edit   | `package.json` + `package-lock.json` (via npm install) |

## Files I will NOT touch
- `services/courtsService.ts` (Google Places — left alone)
- `data/courts.ts` (still used as fallback)
- `database/create_table.sql` (no schema change needed)
- `database/import_courts.py` (no re-import needed)
- `lineofficial/intent.py`, `lineofficial/reply.py` (no changes needed)

---

## Review

### What changed

**Expo app — now reads from Supabase**
| File | Change |
|---|---|
| `package.json` | Added `@supabase/supabase-js` dependency |
| `.env.example` | Documented `EXPO_PUBLIC_SUPABASE_URL` + `EXPO_PUBLIC_SUPABASE_ANON_KEY` |
| `services/supabaseClient.ts` | **New** — single shared Supabase client (or `null` if env missing) |
| `services/courtsSupabaseService.ts` | **New** — `fetchCourtsFromSupabase()` queries `courts` table, maps rows → `Court` interface |
| `hooks/useCourts.ts` | Replaced Google Places + GPS flow with single Supabase call. Mock fallback preserved. |

**LINE bot — bug fixed**
| File | Change |
|---|---|
| `lineofficial/server.py` | `query_courts()`: removed broken `sport_type` SQL filter. Now fetches by province in SQL and filters by sport keywords (matched against `name_en` / `name_th`) in Python. |

### Files NOT touched (intentionally simple)
- `services/courtsService.ts` (Google Places code left as-is)
- `data/courts.ts` (still used as graceful fallback)
- `database/create_table.sql` and `database/import_courts.py` (no schema/data change needed)
- `lineofficial/intent.py` and `lineofficial/reply.py` (no changes needed)

### What the user needs to do to finish

**For the Expo app:**
1. Create `.env` in project root with:
   ```
   EXPO_PUBLIC_SUPABASE_URL=https://YOUR_PROJECT.supabase.co
   EXPO_PUBLIC_SUPABASE_ANON_KEY=eyJ...   ← anon public key, NOT service_role
   ```
2. Run `npx expo start --clear`
3. Open Courts tab → real Thai courts should appear

**For the LINE bot:**
1. Confirm `lineofficial/.env` has `LINE_CHANNEL_SECRET`, `LINE_CHANNEL_ACCESS_TOKEN`, `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`
2. Run `python lineofficial/server.py`
3. In another terminal: `ngrok http 5000`
4. Paste `https://<ngrok>.ngrok.io/webhook` into developers.line.biz → Channel → Messaging API → Webhook URL → **Verify**
5. Toggle **Use webhook** ON and **Auto-reply messages** OFF in the LINE Console
6. Add the bot as friend on phone, send `tennis Bangkok` or `แบดมินตันพิจิตร`

### How the LINE bot bug got fixed (for the student)
The `intent.py` correctly detected sport (tennis/badminton/squash), but the Supabase query tried to filter on a `sport_type` column that was never created in the schema. So a query like "tennis Bangkok" was returning zero rows or erroring out.

**The fix:** since the imported Excel data doesn't include sport-type metadata, the simplest correct approach is to filter in Python by checking whether the court name (English or Thai) contains the sport keyword. No database migration needed — single function change.

### Simplicity check
- 2 new files (~80 lines total), 2 file edits.
- No new abstractions, no shared base classes, no configuration system.
- Preserved the existing mock-fallback pattern; the hook's public API is unchanged so no caller code needed to change.
