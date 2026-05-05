"""Cluster the GDELT shadow-fleet articles by title content and flag wire vs original."""
from __future__ import annotations
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]

for label in ("shadow_fleet_ofac", "ofac_tanker", "shadow_fleet_eu"):
    p = ROOT / "cache" / "gdelt" / f"{label}.parquet"
    if not p.exists():
        continue
    df = pd.read_parquet(p)
    print(f"\n=== {label}: {len(df)} articles ===")
    if df.empty:
        continue
    # Dedupe by domain to compress wire chains
    if "domain" in df.columns:
        df = df.drop_duplicates(subset=["domain"])
        print(f"deduped by domain: {len(df)}")
    # Filter to Russia-related (not Iran)
    if "title" in df.columns:
        russia_mask = df["title"].fillna("").str.contains("Russia|Russian|Sovcomflot|Urals|shadow", case=False, regex=True, na=False)
        iran_mask = df["title"].fillna("").str.contains("Iran|Hormuz|Tehran", case=False, regex=True, na=False)
        russia_only = df[russia_mask & ~iran_mask]
        both = df[russia_mask & iran_mask]
        iran_only = df[iran_mask & ~russia_mask]
        print(f"Russia-only: {len(russia_only)}, Iran-only: {len(iran_only)}, both: {len(both)}, neither: {len(df) - len(russia_only) - len(iran_only) - len(both)}")

        # Show Russia-only article titles
        print("\nRussia-only titles (first 30):")
        cols = [c for c in ("seendate", "domain", "title") if c in russia_only.columns]
        for _, r in russia_only.head(30).iterrows():
            print(f"  [{r.get('seendate', '')}] {r.get('domain', '')}: {r.get('title', '')[:140]}")
