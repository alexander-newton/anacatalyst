"""Fetch GDELT — last 30 days of "shadow fleet" + "OFAC" + "Russia" + "tanker" coverage, pinned window.

Documented in skills/fetching-news-gdelt/SKILL.md.
"""
from __future__ import annotations
import os
import sys
import json
import datetime as dt
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from _safe import safe_get  # noqa: E402

OUT = Path(__file__).resolve().parents[2] / "cache" / "gdelt"
OUT.mkdir(parents=True, exist_ok=True)

GDELT = "https://api.gdeltproject.org/api/v2/doc/doc"
HEADERS = {"User-Agent": "strategic-analyst/0.1 (test)"}


def gdelt_artlist(query: str, start: dt.datetime, end: dt.datetime, max_records: int = 250) -> pd.DataFrame:
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
    try:
        articles = r.json().get("articles", [])
    except Exception:
        articles = []
    return pd.DataFrame(articles)


def main():
    end = dt.datetime(2026, 5, 5, 12, 0, 0, tzinfo=dt.timezone.utc)
    start = end - dt.timedelta(days=30)
    print(f"window: {start.isoformat()} -> {end.isoformat()}")

    queries = {
        "shadow_fleet_ofac": '("shadow fleet" OR "shadow tanker") AND OFAC AND Russia',
        "ofac_tanker": '(OFAC OR "U.S. Treasury") AND tanker AND Russia',
        "shadow_fleet_eu": '"shadow fleet" AND (sanctions OR "price cap")',
    }

    summary = {"accessed_at": dt.datetime.now(dt.timezone.utc).isoformat(),
               "window_start": start.isoformat(),
               "window_end": end.isoformat(),
               "results": {}}
    for label, q in queries.items():
        try:
            df = gdelt_artlist(q, start, end, 250)
            df.to_parquet(OUT / f"{label}.parquet")
            print(f"\n{label}: rows={len(df)}; query: {q}")
            if not df.empty:
                # Dedupe by domain, then show top 15 titles
                if "domain" in df.columns:
                    print("Top 10 domains:")
                    print(df["domain"].value_counts().head(10).to_string())
                cols = [c for c in ("seendate", "domain", "language", "sourcecountry", "title") if c in df.columns]
                deduped = df.drop_duplicates(subset=["domain"]) if "domain" in df.columns else df
                print("\nFirst 15 deduped articles:")
                print(deduped[cols].head(15).to_string(index=False))

                summary["results"][label] = {
                    "rows": int(len(df)),
                    "deduped_domains": int(deduped.shape[0]),
                    "query": q,
                    "top_domains": df["domain"].value_counts().head(5).to_dict() if "domain" in df.columns else {},
                }
            else:
                summary["results"][label] = {"rows": 0, "query": q}
        except Exception as e:
            print(f"{label} fetch failed: {type(e).__name__}: {str(e)[:200]}")
            summary["results"][label] = {"error": f"{type(e).__name__}: {str(e)[:200]}", "query": q}

    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, default=str))


if __name__ == "__main__":
    main()
