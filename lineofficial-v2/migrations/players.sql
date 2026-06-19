-- Tennis Matcher Bot v2 — Players & Matches schema
-- Run this in Supabase SQL Editor before starting server.py.

-- Players: every LINE user who adds the bot as friend gets a row here.
CREATE TABLE IF NOT EXISTS players (
  line_user_id    TEXT PRIMARY KEY,
  nickname        TEXT,
  skill_level     TEXT CHECK (skill_level IN ('beginner', 'casual', 'intermediate', 'competitive')),
  area            TEXT,
  line_basic_id   TEXT,
  status          TEXT NOT NULL DEFAULT 'onboarding'
                       CHECK (status IN ('onboarding', 'active', 'paused')),
  onboarding_step INT  NOT NULL DEFAULT 0,
  registered_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_players_active ON players(status) WHERE status = 'active';
CREATE INDEX IF NOT EXISTS idx_players_area   ON players(area);

-- Matches: a suggested pairing between two players.
CREATE TABLE IF NOT EXISTS matches (
  id               BIGSERIAL PRIMARY KEY,
  player_a_id      TEXT NOT NULL REFERENCES players(line_user_id) ON DELETE CASCADE,
  player_b_id      TEXT NOT NULL REFERENCES players(line_user_id) ON DELETE CASCADE,
  player_a_response TEXT NOT NULL DEFAULT 'pending'
                        CHECK (player_a_response IN ('pending', 'accepted', 'declined')),
  player_b_response TEXT NOT NULL DEFAULT 'pending'
                        CHECK (player_b_response IN ('pending', 'accepted', 'declined')),
  introduced       BOOLEAN NOT NULL DEFAULT FALSE,
  suggested_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_matches_player_a ON matches(player_a_id);
CREATE INDEX IF NOT EXISTS idx_matches_player_b ON matches(player_b_id);
