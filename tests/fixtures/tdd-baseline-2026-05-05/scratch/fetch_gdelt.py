"""Last-30-day GDELT artlist coverage for 'shadow fleet' + Russia + tanker + OFAC.

Per skills/fetching-news-gdelt/SKILL.md.
"""
from __future__ import annotations

import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd

from _safe import safe_get

OUT = Path(__file__).resolve().parent.parent.parent / "cache" / "gdelt"
OUT.mkdir(parents=True, exist_ok=True)
HEADERS = {"User-Agent": "strategic-analyst/0.1 integration-test (russia-shadow-fleet)"}

GDELT = "https://api.gdeltproject.org/api/v2/doc/doc"


def artlist(query: str, start: datetime, end: datetime, max_records: int = 250) -> pd.DataFrame:
    fmt = "%Y%m%d%H%M%S"
    params = {
        "query": query,
        "mode": "artlist",
        "format": "json",
        "startdatetime": start.strftime(fmt),
        "enddatetime": end.strftime(fmt),
        "maxrecords": max_records,
        "sort": "datedesc",
    }
    r = safe_get(GDELT, params=params, headers=HEADERS, timeout=30)
    return pd.DataFrame(r.json().get("articles", []))


def timeline(query: str, start: datetime, end: datetime, mode: str) -> pd.DataFrame:
    fmt = "%Y%m%d%H%M%S"
    params = {
        "query": query,
        "mode": mode,
        "format": "json",
        "startdatetime": start.strftime(fmt),
        "enddatetime": end.strftime(fmt),
    }
    r = safe_get(GDELT, params=params, headers=HEADERS, timeout=30)
    j = r.json()
    return pd.DataFrame(j.get("timeline", [{}])[0].get("data", []))


def main() -> int:
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=30)
    query = '("shadow fleet" OR "dark fleet" OR "ghost fleet") AND (Russia OR Russian) AND (OFAC OR Treasury OR sanctions) AND (tanker OR vessel OR oil)'
    print(f"[gdelt] window {start.isoformat()} - {end.isoformat()}", file=sys.stderr)
    print(f"[gdelt] query: {query}", file=sys.stderr)

    # 30 days at once is too long for artlist; slice into 6-day windows
    all_rows = []
    cursor = start
    while cursor < end:
        slice_end = min(cursor + timedelta(days=6), end)
        try:
            df = artlist(query, cursor, slice_end, max_records=250)
            all_rows.append(df)
            print(f"[gdelt] {cursor.date()} - {slice_end.date()}: {len(df)} rows",
                  file=sys.stderr)
        except Exception as e:
            print(f"[gdelt] slice {cursor.date()} errored: {type(e).__name__}: {e}",
                  file=sys.stderr)
        cursor = slice_end
        time.sleep(1)

    if all_rows:
        all_df = pd.concat(all_rows, ignore_index=True)
        all_df.to_parquet(OUT / "shadow_fleet_30d.parquet")
        # Domain dedup
        if "domain" in all_df.columns:
            top_domains = all_df["domain"].value_counts().head(20)
            print("\n[gdelt] top 20 domains:", file=sys.stderr)
            print(top_domains.to_string(), file=sys.stderr)
        if "language" in all_df.columns:
            print("\n[gdelt] languages:", file=sys.stderr)
            print(all_df["language"].value_counts().head(15).to_string(), file=sys.stderr)
        if "sourcecountry" in all_df.columns:
            print("\n[gdelt] source countries:", file=sys.stderr)
            print(all_df["sourcecountry"].value_counts().head(15).to_string(), file=sys.stderr)

    # Volume timeline
    try:
        vol = timeline(query, start, end, "timelinevol")
        vol.to_csv(OUT / "shadow_fleet_volume.csv", index=False)
        print(f"\n[gdelt] volume timeline rows: {len(vol)}", file=sys.stderr)
    except Exception as e:
        print(f"[gdelt] volume errored: {type(e).__name__}: {e}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
