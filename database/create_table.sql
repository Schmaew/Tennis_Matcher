DROP TABLE IF EXISTS courts;

CREATE TABLE courts (
  id                 BIGSERIAL PRIMARY KEY,
  province           TEXT,
  name_en            TEXT,
  name_th            TEXT,
  location           TEXT,
  google_maps_url    TEXT,
  phone              TEXT,
  line_id            TEXT,
  facebook           TEXT,
  gmaps_verified_url TEXT,
  stars              NUMERIC(3,1),
  reviews            INTEGER,
  lat                NUMERIC(11,7),
  lng                NUMERIC(11,7),
  created_at         TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE (name_en, province)
);

CREATE INDEX IF NOT EXISTS idx_courts_province ON courts (province);

CREATE INDEX IF NOT EXISTS idx_courts_latng ON courts (lat, lng)
  WHERE lat IS NOT NULL;