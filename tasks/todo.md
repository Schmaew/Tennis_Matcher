# Fix errors in `anti_pantip_pantip_club/pantip_addcomment.py`

## Bugs I found (in order of severity)

### 1. `db_fetch_pending_topics` re-fetches topics the user already marked "not send"
`db_mark_not_send` sets `process_status = "n"` but leaves `messages` NULL. `db_fetch_pending_topics` filters only by `messages is null`, so a topic the user said "n" to last run shows up again next run.
**Fix:** add `.eq("process_status", "u")` to the fetch query so only un-processed topics come back.

### 2. `submit_btn.get_attribute("class")` can return `None` → `TypeError`
Line 470: `if "disabled" not in submit_btn.get_attribute("class")` — if the element has no `class` attribute, `get_attribute` returns `None` and `"disabled" not in None` raises `TypeError`.
**Fix:** coerce to empty string: `(submit_btn.get_attribute("class") or "")`.

### 3. `db_check_exists` has no error handling
Line 212-214. If Supabase errors (network blip, rate limit), the whole `find` loop crashes mid-scan and loses progress.
**Fix:** wrap in try/except, return `False` on error so the loop continues (worst case = a re-insert that the unique key would reject).

### 4. Chrome singleton lock not cleaned up on startup
You hit this twice today. If the previous run was Ctrl-C'd, `pantip_bot_profile/SingletonLock` etc. remain and the next launch fails with `session not created: Chrome instance exited`.
**Fix:** before `webdriver.Chrome(...)`, remove `SingletonLock`, `SingletonCookie`, `SingletonSocket` from the profile dir if they exist.

### 5. `driver.quit()` never called → Chrome process leaks on normal exit
After `run_find_mode` / `run_send_mode` returns, `main()` exits without quitting the driver. The Chrome window stays open and the profile stays locked, which causes bug #4 next run.
**Fix:** wrap the work in `try / finally: driver.quit()`.

### 6. `python-dotenv` missing from `requirements.txt`
Script does `from dotenv import load_dotenv` but the package is only pulled transitively via `webdriver-manager`. If that dep ever changes, the script breaks.
**Fix:** add `python-dotenv` to `requirements.txt`.

## Not fixing (out of scope unless you say so)
- Duplicate constants at lines 27-32 vs 35-39 (`KEYWORD`/`TARGET_KEYWORD`/`COOLDOWN_*`/`IMAGE_FOLDER` redeclared — second copy is unused). Cosmetic, not a bug.
- `driver.back()` after each topic visit loses infinite-scroll position. Performance, not correctness.
- Module-level `exit(1)` on missing env vars prevents test imports. Minor.

## Todo
- [x] Fix #1 — add `process_status = "u"` filter in `db_fetch_pending_topics`
- [x] Fix #2 — null-safe class check on submit button
- [x] Fix #3 — try/except in `db_check_exists`
- [x] Fix #4 — clear singleton locks before launching Chrome
- [x] Fix #5 — try/finally with `driver.quit()` in `main`
- [x] Fix #6 — add `python-dotenv` to `requirements.txt`
- [x] Fix #7 — pointed Pylance at the correct interpreter (IDE yellow underlines)

## Review

### Files changed
| File | Change |
|---|---|
| `anti_pantip_pantip_club/pantip_addcomment.py` | 5 surgical edits (bugs #1–#5) |
| `anti_pantip_pantip_club/requirements.txt` | Added `python-dotenv` (#6) |
| `.vscode/settings.json` | Added `python.defaultInterpreterPath` so Pylance resolves selenium/supabase imports (#7) |

### What each edit does
1. **`db_fetch_pending_topics`** now filters `.eq("process_status", "u")` so topics the user typed "n" on no longer reappear next run.
2. **Submit button class check** is now null-safe — `(submit_btn.get_attribute("class") or "")` — no more `TypeError` if Pantip's button renders without a `class` attribute.
3. **`db_check_exists`** wrapped in try/except. Supabase errors during scan now log a warning and skip instead of killing the entire `find` loop.
4. **Singleton lock cleanup** at the top of `main()` — removes `SingletonLock`, `SingletonCookie`, `SingletonSocket` from `pantip_bot_profile/` before launching Chrome. Self-heals after a Ctrl-C.
5. **`try/finally` with `driver.quit()`** wraps the find/send work so Chrome always closes — no more orphan Chrome processes locking the profile.
6. **`python-dotenv`** declared explicitly — no longer relying on a transitive pull from `webdriver-manager`.
7. **`python.defaultInterpreterPath`** in `.vscode/settings.json` points Pylance at `/Library/Frameworks/Python.framework/Versions/3.11/bin/python3`, where the packages actually live. The yellow squiggles on `from selenium import ...` etc. were Pylance using `/usr/bin/python3` (forced by the existing `python-envs.defaultEnvManager: ms-python.python:system` line), which has no selenium installed.

### Verification
- `python3 -m py_compile pantip_addcomment.py` → clean
- All edits are <10 lines each, no refactors, no new abstractions

### What the user should do
- **Reload the VS Code window** (Cmd+Shift+P → "Developer: Reload Window") for Pylance to pick up the new interpreter path. The yellow underlines on lines 7–15 will go away after the reload.
- Re-run with `python3 anti_pantip_pantip_club/pantip_addcomment.py find 5` to confirm.

### Not changed (per scope)
- Duplicate constants at lines 27-32 vs 35-39
- `driver.back()` infinite-scroll position loss
- Module-level `exit(1)` on missing env vars
