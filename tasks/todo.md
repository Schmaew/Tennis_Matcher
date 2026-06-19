# Parallel matching + waiting queue

## What you asked for
1. **Parallel matching** — when a user types `หาคู่`, push the match invite to the **top N candidates at once**. First mutual accept wins; the others get auto-declined.
2. **Priority/waiting-queue table** — when no candidates exist right now, store the requester in a FIFO queue. When a new compatible user becomes active, auto-match the longest-waiting person.

## Part A — Parallel matching (N invites simultaneously)

### Files I'll touch
| File | Change |
|---|---|
| `matching.py` | Add `find_top_n_partners(player, n=3)` that returns the top-N ranked candidates (uses the same `_score`). Keep `find_best_partner` for backward compat. |
| `server.py:_find_partner` | Loop over the top-N list, `db.create_match()` for each, push card to each candidate. Reply to the caller with **one** summary message ("ส่งคำขอให้ N คน รอใครตอบรับก่อน"). |
| `matching.py:handle_match_response` | When a match reaches **both accepted**, look up all other non-introduced matches involving either side, set them `declined` and push the unlucky candidates a "อีกฝ่ายเจอคู่ตีคนอื่นไปแล้ว" message + 🎾 หาคู่ใหม่ button. |
| `messages.py` | New strings `MATCH_PARALLEL_SENT(n)`, `MATCH_CANCELED_OTHER`. |

### Knobs
- `PARALLEL_MATCH_N` env var (default `3`)

## Part B — Waiting queue with FIFO priority

### New table
```sql
CREATE TABLE IF NOT EXISTS waiting_queue (
  id            BIGSERIAL PRIMARY KEY,
  line_user_id  TEXT NOT NULL UNIQUE REFERENCES players(line_user_id) ON DELETE CASCADE,
  queued_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_waiting_queue_queued_at ON waiting_queue(queued_at);
```
Stored in **new** `migrations/add_waiting_queue.sql` — you'd run it once in Supabase SQL Editor.

### Files I'll touch
| File | Change |
|---|---|
| `db.py` | `enqueue_waiting(user_id)`, `dequeue_waiting(user_id)`, `get_waiting_queue()` (FIFO via `ORDER BY queued_at ASC`). |
| `server.py:_find_partner` | If parallel search returns 0 candidates → `db.enqueue_waiting(player)`, reply `WAITING_QUEUED`. |
| `matching.py` | `try_match_from_queue(line_api, new_active_user)` — walk the queue in FIFO order, find the first waiter compatible with the new user, trigger a parallel match for the waiter, dequeue the waiter. |
| `onboarding.py:_step5_confirm_basic_id` | After flipping `status='active'`, call `matching.try_match_from_queue(line_api, player)`. |
| `messages.py` | `WAITING_QUEUED` string. |

## What I will NOT touch (out of scope)
- The expiration thread — its decline behavior already plays nicely with parallel matches (a stale parallel invite just becomes a declined match).
- Skill/area-weighted priority for the queue — you picked FIFO only.
- Admin UI for the queue.

## Once you say go, my todos
- [ ] Part A: `find_top_n_partners` + caller loop + auto-cancel of losers
- [ ] Part A: messages
- [ ] Part B: migration SQL file
- [ ] Part B: `db.py` queue helpers
- [ ] Part B: `_find_partner` enqueue on no candidates
- [ ] Part B: `try_match_from_queue` + hook in onboarding step 5
- [ ] Restart server, smoke-test
- [ ] Tell you to run the new migration SQL

## Two clarifying things before I start

1. **Self-cancel scope** — when match A↔B completes (both accepted), should we cancel other matches where **A** is involved, where **B** is involved, or both? I'm assuming **both** (cleanest).
2. **Queue trigger** — only triggers on a NEW active user (just finished onboarding)? Or also when an existing paused user resumes, or when a player just declined a match (now free again)?
