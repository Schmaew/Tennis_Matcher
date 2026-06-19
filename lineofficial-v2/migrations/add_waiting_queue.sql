-- FIFO waiting queue. A player who hits "no candidates" goes in here;
-- next time a new compatible user becomes active, the oldest waiter wins.
-- Run once in the Supabase SQL editor; safe to re-run.

CREATE TABLE IF NOT EXISTS waiting_queue (
  id            BIGSERIAL PRIMARY KEY,
  line_user_id  TEXT NOT NULL UNIQUE REFERENCES players(line_user_id) ON DELETE CASCADE,
  queued_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_waiting_queue_queued_at ON waiting_queue(queued_at);
