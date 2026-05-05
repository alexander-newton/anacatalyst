"""Pull OFAC SDN list and the recent-actions RSS, search for Russia-program vessel
entries (shadow-fleet tankers).

Per skills/fetching-ofac-sanctions/SKILL.md and skills/handling-credentials-safely/SKILL.md.
"""
from __future__ import annotations

import sys
from io import StringIO
from pathlib import Path

import httpx
import pandas as pd
import feedparser

from _safe import safe_get, redact_url

OUT = Path(__file__).resolve().parent.parent.parent / "cache" / "ofac"
OUT.mkdir(parents=True, exist_ok=True)

SDN_URL = "https://sanctionslistservice.ofac.treas.gov/api/publicationpreview/exports/sdn.csv"
RSS_URL = "https://ofac.treasury.gov/recent-actions/recent-actions-rss-feed"
HEADERS = {"User-Agent": "strategic-analyst/0.1 integration-test"}

SDN_COLS = ["ent_num", "name", "sdn_type", "program", "title", "call_sign",
            "vess_type", "tonnage", "grt", "vess_flag", "vess_owner", "remarks"]


def fetch_sdn() -> pd.DataFrame:
    print("[ofac] fetching SDN list...", file=sys.stderr)
    r = safe_get(SDN_URL, timeout=120, follow_redirects=True, headers=HEADERS)
    df = pd.read_csv(StringIO(r.text), header=None, names=SDN_COLS,
                     quotechar='"', encoding="latin-1", on_bad_lines="skip")
    print(f"[ofac] SDN rows: {len(df)}", file=sys.stderr)
    df.to_parquet(OUT / "sdn.parquet")
    return df


def fetch_recent_actions():
    print("[ofac] fetching recent-actions RSS...", file=sys.stderr)
    r = safe_get(RSS_URL, timeout=60, headers=HEADERS, follow_redirects=True)
    feed = feedparser.parse(r.text)
    rows = []
    for e in feed.entries:
        rows.append({
            "title": e.get("title", ""),
            "link": e.get("link", ""),
            "published": e.get("published", ""),
            "summary": e.get("summary", "")[:500],
        })
    df = pd.DataFrame(rows)
    df.to_parquet(OUT / "recent_actions.parquet")
    print(f"[ofac] recent-actions items: {len(df)}", file=sys.stderr)
    return df


def main() -> int:
    sdn = fetch_sdn()
    rss = fetch_recent_actions()

    # Russia program vessels (shadow-fleet candidates)
    russia_progs = sdn["program"].astype(str).str.contains("RUSSIA", case=False, na=False)
    vessel_rows = sdn["sdn_type"].astype(str).str.contains("vessel", case=False, na=False)
    russia_vessels = sdn[russia_progs & vessel_rows].copy()
    print(f"[ofac] Russia-program vessel rows: {len(russia_vessels)}", file=sys.stderr)
    russia_vessels.to_parquet(OUT / "russia_vessels.parquet")

    # Also: any vessel entry whose remarks/owner mentions Russia
    russia_text = (
        sdn["remarks"].astype(str).str.contains("russia", case=False, na=False)
        | sdn["vess_flag"].astype(str).str.contains("russia", case=False, na=False)
        | sdn["vess_owner"].astype(str).str.contains("russia", case=False, na=False)
    )
    russia_text_vessels = sdn[vessel_rows & russia_text]
    print(f"[ofac] Vessel entries with Russia in remarks/flag/owner: {len(russia_text_vessels)}",
          file=sys.stderr)
    russia_text_vessels.to_parquet(OUT / "russia_vessels_text.parquet")

    # Program breakdown for vessel rows
    vessel_progs = sdn[vessel_rows]["program"].value_counts().head(20)
    print("[ofac] top programs for vessel-type SDN rows:", file=sys.stderr)
    print(vessel_progs.to_string(), file=sys.stderr)

    # Russia-tagged recent actions
    rss["lower"] = (rss["title"] + " " + rss["summary"]).str.lower()
    russia_rss = rss[rss["lower"].str.contains("russia|shadow|fleet|tanker|maritime|oil", na=False)]
    print(f"\n[ofac] recent-actions matching russia/shadow/fleet/tanker/maritime/oil: "
          f"{len(russia_rss)}", file=sys.stderr)
    for _, row in russia_rss.head(15).iterrows():
        print(f"  - {row['published']}: {row['title']}", file=sys.stderr)

    # Print a sample of Russia-program vessels
    print("\n[ofac] sample Russia-program vessel rows:", file=sys.stderr)
    cols = ["name", "program", "vess_type", "tonnage", "vess_flag", "remarks"]
    available = [c for c in cols if c in russia_vessels.columns]
    sample = russia_vessels[available].head(15)
    for _, r in sample.iterrows():
        print(
            f"  {r.get('name','?')[:40]:40s}  prog={str(r.get('program',''))[:25]:25s}"
            f"  flag={str(r.get('vess_flag',''))[:15]:15s}",
            file=sys.stderr,
        )

    print(f"\n[ofac] saved to {OUT}/", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
