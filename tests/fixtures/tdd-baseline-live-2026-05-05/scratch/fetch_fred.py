"""Fetch FRED series — DEXUSEU, RTWEXBGS, DCOILBRENTEU. Note: TTF is NOT in FRED.

Documented in skills/fetching-fred-macro/SKILL.md.
"""
from __future__ import annotations
import os
import sys
import json
import datetime as dt
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent))
from _safe import safe_get, confirm_key  # noqa: E402

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

OUT = Path(__file__).resolve().parents[2] / "cache" / "fred"
OUT.mkdir(parents=True, exist_ok=True)

KEY = os.environ["FRED_API_KEY"]
FRED = "https://api.stlouisfed.org/fred"

SERIES = {
    "DEXUSEU": "USD per EUR (daily)",
    "RTWEXBGS": "Real broad-trade-weighted USD index (monthly)",
    "DCOILBRENTEU": "Brent crude (daily, $/bbl)",
}


def fred_series(series_id: str, start: str = "2022-01-01") -> pd.DataFrame:
    r = safe_get(
        f"{FRED}/series/observations",
        params={
            "series_id": series_id,
            "api_key": KEY,
            "file_type": "json",
            "observation_start": start,
        },
        timeout=30,
    )
    obs = r.json()["observations"]
    df = pd.DataFrame(obs)
    if df.empty:
        return df
    df["date"] = pd.to_datetime(df["date"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    return df.set_index("date")[["value"]].rename(columns={"value": series_id})


def fred_meta(series_id: str) -> dict:
    r = safe_get(
        f"{FRED}/series",
        params={"series_id": series_id, "api_key": KEY, "file_type": "json"},
        timeout=30,
    )
    return r.json()["seriess"][0]


def main():
    confirm_key("FRED_API_KEY", KEY)
    summary = {"accessed_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    for sid, label in SERIES.items():
        try:
            df = fred_series(sid)
            meta = fred_meta(sid)
            df.to_parquet(OUT / f"{sid}.parquet")
            df_clean = df.dropna()
            latest_date = df_clean.index.max() if not df_clean.empty else None
            latest_val = df_clean[sid].iloc[-1] if not df_clean.empty else None
            print(f"\n{sid} — {label}: rows={len(df)}, last={latest_date}, val={latest_val}, units={meta.get('units_short')}")
            print(df_clean.tail(5).to_string())
            summary[sid] = {
                "rows": int(len(df)),
                "latest_date": str(latest_date.date()) if latest_date is not None else None,
                "latest_value": float(latest_val) if latest_val is not None and pd.notna(latest_val) else None,
                "units": meta.get("units_short"),
                "frequency": meta.get("frequency_short"),
                "last_updated": meta.get("last_updated"),
                "label": label,
            }
        except Exception as e:
            print(f"{sid} fetch failed: {type(e).__name__}: {str(e)[:200]}")
            summary[sid] = {"error": f"{type(e).__name__}: {str(e)[:200]}", "label": label}

    # Note explicitly: TTF / NBP gas benchmarks are NOT in FRED. Document the gap.
    summary["TTF_NBP_NOTE"] = "TTF/NBP European gas benchmarks are not in FRED — see skill silent-substitution warning. ICE Endex / EEX is the upstream source."
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, default=str))
    print(f"\nsummary.json saved")


if __name__ == "__main__":
    main()
