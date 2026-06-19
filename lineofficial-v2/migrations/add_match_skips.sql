-- Tracks how many times one player has skipped another so the matcher
-- can deprioritize repeated skips.
-- Run once in the Supabase SQL editor; safe to re-run.

CREATE TABLE IF NOT EXISTS match_skips (
  skipper_id  TEXT NOT NULL REFERENCES players(line_user_id) ON DELETE CASCADE,
  skipped_id  TEXT NOT NULL REFERENCES players(line_user_id) ON DELETE CASCADE,
  count       INT  NOT NULL DEFAULT 1,
  updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (skipper_id, skipped_id)
);

CREATE INDEX IF NOT EXISTS idx_match_skips_skipper ON match_skips(skipper_id);
