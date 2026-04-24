"""
import_courts.py
================================================================
Reads Excel sheet -> extracts or geocodes lat/lng via Nominatim
(OpenStreetMap) -> upserts all rows into Supabase.

Usage:
    python import_courts.py

Required .env variables:
    SUPABASE_URL=https://xxxx.supabase.co
    SUPABASE_SERVICE_KEY=eyJ...

No Google Maps API key needed. Nominatim is free with no signup.
================================================================
"""

import os, re, time, sys
import pandas as pd
import httpx
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

# -- Config ---------------------------------------------------
EXCEL_FILE        = "TennisMatching.xlsx"
SHEET_NAME        = "Research - All Courts"
SUPABASE_URL      = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY      = os.getenv("SUPABASE_SERVICE_KEY", "")
GEOCODE_DELAY_SEC = 1.1   # Nominatim enforces max 1 req/sec
BATCH_SIZE        = 50    # rows per upsert call

# -- Supabase client ------------------------------------------
if not SUPABASE_URL or not SUPABASE_KEY:
    print("ERROR: Set SUPABASE_URL and SUPABASE_SERVICE_KEY in .env")
    sys.exit(1)

sb = create_client(SUPABASE_URL, SUPABASE_KEY)


# -- 1. Extract lat/lng directly from a Google Maps URL -------
def extract_from_url(url: str):
    """
    Returns (lat, lng) if the URL contains embedded coordinates,
    otherwise returns (None, None).

    Supported formats:
      @13.7326,100.5608      (standard share URL)
      !3d13.7326!4d100.5608  (embed URL)
    """
    if not isinstance(url, str):
        return None, None

    m = re.search(r"@(-?\d+\.\d+),(-?\d+\.\d+)", url)
    if m:
        return float(m.group(1)), float(m.group(2))

    m = re.search(r"!3d(-?\d+\.\d+)!4d(-?\d+\.\d+)", url)
    if m:
        return float(m.group(1)), float(m.group(2))

    return None, None


# -- 2. Geocode a text query via Nominatim (OpenStreetMap) ----
def geocode(query: str):
    """
    Sends a free-text query to Nominatim and returns (lat, lng).
    Tries up to 3 progressively shorter queries before giving up.
    Returns (None, None) if all attempts fail.
    """
    if not query.strip():
        return None, None

    # Build a list of fallback queries from long to short.
    # Nominatim struggles with long Thai addresses, so we retry
    # with just the name, then name + province.
    parts   = query.split(" Thailand")[0].strip()
    tokens  = parts.split()
    queries = [query]

    # Fallback 1: first 4 words + Thailand
    if len(tokens) > 4:
        queries.append(" ".join(tokens[:4]) + " Thailand")

    # Fallback 2: first 2 words only + Thailand
    if len(tokens) > 2:
        queries.append(" ".join(tokens[:2]) + " Thailand")

    for q in queries:
        try:
            resp = httpx.get(
                "https://nominatim.openstreetmap.org/search",
                params={
                    "q":              q,
                    "format":         "json",
                    "limit":          1,
                    "countrycodes":   "th",
                    "addressdetails": 0,
                },
                headers={"User-Agent": "TennisMatcher/1.0 (import script)"},
                timeout=10,
            )
            results = resp.json()
            if results:
                return float(results[0]["lat"]), float(results[0]["lon"])
            time.sleep(GEOCODE_DELAY_SEC)  # still need to rate-limit between retries
        except Exception as e:
            print(f"  [geocode] error on '{q[:50]}': {e}")

    print(f"  [geocode] no result for: {queries[0][:70]}")
    return None, None


# -- 3. Build the best geocode query from available row data --
def build_geocode_query(row: dict) -> str:
    """
    Priority order:
      1. Extract search term from GMaps_Verified_URL if it is a
         /maps/search/ URL (most specific)
      2. English name + province (short, works better with Nominatim)
      3. Thai name + province
      4. English name alone
    """
    name_en  = str(row.get("Name (English)") or "").strip()
    name_th  = str(row.get("ชื่อ (ไทย)")    or "").strip()
    province = str(row.get("Province")       or "").strip()

    # Pull search term embedded in the verified URL when available
    gmaps_url = str(row.get("GMaps_Verified_URL") or "")
    url_q = re.search(r"/maps/search/([^/?]+)", gmaps_url)
    if url_q:
        return url_q.group(1).replace("+", " ") + " Thailand"

    # Shorter queries work better with Nominatim for Thai locations.
    # name + province is usually enough to find the right place.
    if name_en and province:
        return f"{name_en} {province} Thailand"
    if name_th and province:
        return f"{name_th} {province} Thailand"
    if name_en:
        return f"{name_en} Thailand"
    return f"{name_th} Thailand"


# -- 4. Safely parse numeric fields from Excel ----------------
def safe(v):
    """Converts NaN / None / empty string to None."""
    if v is None:
        return None
    if isinstance(v, float) and pd.isna(v):
        return None
    s = str(v).strip()
    return s if s else None


def safe_float(v):
    """
    Converts a value to float, returning None on failure.
    Handles cases where Excel cells contain text instead of numbers
    (e.g. a Facebook URL accidentally placed in the Stars column).
    """
    if v is None:
        return None
    try:
        f = float(v)
        return None if pd.isna(f) else f
    except (ValueError, TypeError):
        return None


def safe_int(v):
    """Converts a value to int, returning None on failure."""
    if v is None:
        return None
    try:
        f = float(v)
        return None if pd.isna(f) else int(f)
    except (ValueError, TypeError):
        return None


# -- 5. Convert a raw Excel row to a Supabase record dict -----
def map_row(row: pd.Series) -> dict:
    return {
        "province":           safe(row.get("Province")),
        "name_en":            safe(row.get("Name (English)")),
        "name_th":            safe(row.get("ชื่อ (ไทย)")),
        "location":           safe(row.get("Location")),
        "google_maps_url":    safe(row.get("Google Maps")),
        "phone":              safe(row.get("Phone")),
        "line_id":            safe(row.get("Line")),
        "facebook":           safe(row.get("Facebook")),
        "gmaps_verified_url": safe(row.get("GMaps_Verified_URL")),
        "stars":              safe_float(row.get("Stars")),
        "reviews":            safe_int(row.get("Reviews")),
        "lat":                None,
        "lng":                None,
    }


# -- 6. Upsert a batch of records into Supabase ---------------
def upsert_batch(records: list):
    """
    Inserts or updates rows using (name_en, province) as the
    conflict key, so re-running the script is safe.
    """
    sb.table("courts") \
      .upsert(records, on_conflict="name_en,province") \
      .execute()


# -- Main -----------------------------------------------------
def main():
    print(f"Reading: {EXCEL_FILE} (sheet: {SHEET_NAME})")
    df = pd.read_excel(EXCEL_FILE, sheet_name=SHEET_NAME)
    print(f"Rows found: {len(df)}")
    print("Geocoding via Nominatim (OpenStreetMap) - no API key required")
    print("Each missing coordinate retries with shorter queries automatically\n")

    records  = []
    from_url = 0
    geocoded = 0
    skipped  = 0
    total    = len(df)

    for i, (_, row) in enumerate(df.iterrows(), 1):
        rec = map_row(row)

        # Try to pull coordinates directly from URL first (free, instant)
        lat, lng = extract_from_url(str(row.get("GMaps_Verified_URL") or ""))
        if lat is None:
            lat, lng = extract_from_url(str(row.get("Google Maps") or ""))

        if lat is not None:
            rec["lat"], rec["lng"] = lat, lng
            from_url += 1
            tag = f"[URL]  lat={lat:.6f}  lng={lng:.6f}"

        else:
            # Geocode with automatic short-query fallback
            query = build_geocode_query(row)
            lat, lng = geocode(query)
            time.sleep(GEOCODE_DELAY_SEC)

            if lat is not None:
                rec["lat"], rec["lng"] = lat, lng
                geocoded += 1
                tag = f"[GEO]  lat={lat:.6f}  lng={lng:.6f}"
            else:
                skipped += 1
                tag = "[NONE] no coordinates"

        name_label = (rec["name_en"] or rec["name_th"] or "-")[:45]
        print(f"[{i:3}/{total}]  {tag}  {name_label}")

        records.append(rec)

        # Upsert in batches to avoid large single payloads
        if len(records) >= BATCH_SIZE:
            upsert_batch(records)
            print(f"         upserted {len(records)} rows to Supabase\n")
            records = []

    # Flush remaining rows
    if records:
        upsert_batch(records)
        print(f"\n         upserted {len(records)} rows to Supabase")

    print(f"""
Done.
  From URL : {from_url:>4} rows
  Geocoded : {geocoded:>4} rows
  No coords: {skipped:>4} rows
  Total    : {total:>4} rows
""")


if __name__ == "__main__":
    main()
