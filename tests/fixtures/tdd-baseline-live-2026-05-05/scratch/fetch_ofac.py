"""Fetch OFAC SDN CSV + recent-actions RSS, search for Russia-program vessel designations.

Documented in skills/fetching-ofac-sanctions/SKILL.md (verified URL note 2026-05).
"""
from __future__ import annotations
import os
import sys
import json
import datetime as dt
from io import StringIO
from pathlib import Path

import httpx
import pandas as pd
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent))
from _safe import safe_get, confirm_key  # noqa: E402

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

OUT = Path(__file__).resolve().parents[2] / "cache" / "ofac"
OUT.mkdir(parents=True, exist_ok=True)

UA = {"User-Agent": "strategic-analyst/0.1 (test)"}

SDN_HEADERS = [
    "ent_num", "name", "sdn_type", "program", "title", "call_sign",
    "vess_type", "tonnage", "grt", "vess_flag", "vess_owner", "remarks",
]

CANONICAL_SDN = "https://sanctionslistservice.ofac.treas.gov/api/publicationpreview/exports/sdn.csv"
LEGACY_SDN = "https://www.treasury.gov/ofac/downloads/sdn.csv"
RECENT_RSS = "https://ofac.treasury.gov/recent-actions/recent-actions-rss-feed"


def fetch_sdn() -> pd.DataFrame:
    # Try canonical, fall back to legacy with redirects
    for url in (CANONICAL_SDN, LEGACY_SDN):
        try:
            r = safe_get(url, timeout=90, follow_redirects=True, headers=UA)
            df = pd.read_csv(
                StringIO(r.text),
                header=None,
                names=SDN_HEADERS,
                quotechar='"',
                encoding="latin-1",
                on_bad_lines="skip",
                low_memory=False,
            )
            print(f"sdn fetched from {url.split('/')[2]}, rows={len(df)}")
            return df
        except Exception as e:
            print(f"sdn fetch failed for {url.split('/')[2]}: {type(e).__name__}: {e}")
            continue
    raise SystemExit("both SDN URLs failed")


def fetch_rss() -> str:
    r = safe_get(RECENT_RSS, timeout=30, follow_redirects=True, headers=UA)
    return r.text


def main():
    print("=== OFAC SDN + recent-actions fetch ===")
    df = fetch_sdn()
    df.to_parquet(OUT / "sdn.parquet")

    # Total programs distribution
    programs = df["program"].fillna("").astype(str)
    russia_mask = programs.str.contains("RUSSIA", case=False, na=False)
    russia = df[russia_mask].copy()
    print(f"total SDN entries: {len(df)}")
    print(f"entries with RUSSIA in program: {len(russia)}")

    # Vessels under Russia-program
    russia_vessels = russia[russia["sdn_type"].fillna("").str.upper().str.contains("VESSEL", na=False)]
    print(f"Russia-program vessels in SDN: {len(russia_vessels)}")

    # Sample vessel rows
    if len(russia_vessels) > 0:
        sample = russia_vessels.head(20)[["ent_num", "name", "program", "sdn_type", "vess_flag", "call_sign"]]
        print("\nFirst 20 Russia-program vessel rows:")
        print(sample.to_string(index=False))

    # Save Russia subset
    russia_vessels.to_csv(OUT / "russia_vessels.csv", index=False)
    russia.to_csv(OUT / "russia_all.csv", index=False)

    # Program-level breakdown
    print("\nRussia-related program distribution (top):")
    print(russia["program"].value_counts().head(20).to_string())

    # Recent actions RSS — fetch + parse a few items
    try:
        rss = fetch_rss()
        # Cheap parse without lxml dependency
        import re
        titles = re.findall(r"<title>(.*?)</title>", rss)[:25]
        dates = re.findall(r"<pubDate>(.*?)</pubDate>", rss)[:25]
        print("\nRecent-actions RSS — top items:")
        for t, d in zip(titles[:15], dates[:15]):
            print(f"  [{d}] {t[:120]}")
        (OUT / "recent_rss.xml").write_text(rss, encoding="utf-8")
        print(f"\nrecent_rss.xml saved, {len(rss)} bytes")
    except Exception as e:
        print(f"RSS fetch failed: {type(e).__name__}: {str(e)[:200]}")

    # Identify recent (last ~365 days) vessel-related Russia designations from rss
    metadata = {
        "accessed_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "sdn_total": int(len(df)),
        "russia_total_entries": int(len(russia)),
        "russia_vessels": int(len(russia_vessels)),
        "canonical_url_used": CANONICAL_SDN,
    }
    (OUT / "summary.json").write_text(json.dumps(metadata, indent=2))
    print(f"\nsummary.json: {metadata}")


if __name__ == "__main__":
    confirm_key("OPENSANCTIONS_KEY", os.environ.get("OPENSANCTIONS_KEY"))
    main()
