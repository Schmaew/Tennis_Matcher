-- Add `line_basic_id` so matched players can contact each other directly.
-- Run once in the Supabase SQL editor; safe to re-run.

ALTER TABLE players ADD COLUMN IF NOT EXISTS line_basic_id TEXT;
