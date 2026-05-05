"""Fetch EIA series — WTI, Brent, US crude inventory weekly, refinery utilisation.

Documented in skills/fetching-eia-energy/SKILL.md.
"""
from __future__ import annotations
import os
import sys
import json
import datetime as dt
from pathlib import Path

import httpx
import pandas as pd
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent))
from _safe import safe_get, confirm_key  # noqa: E402

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

OUT = Path(__file__).resolve().parents[2] / "cache" / "eia"
OUT.mkdir(parents=True, exist_ok=True)

KEY = os.environ["EIA_API_KEY"]
UA = {"User-Agent": "strategic-analyst/0.1 (test)"}

SERIES = {
    "PET.RWTC.D": "WTI Cushing daily ($/bbl)",
    "PET.RBRTE.D": "Brent FOB daily ($/bbl)",
    "PET.WCESTUS1.W": "US crude commercial inventory ex-SPR weekly (kbbl)",
    "PET.WPULEUS3.W": "US refinery utilisation weekly (%)",
}


def eia_series(series_id: str) -> pd.DataFrame:
    r = safe_get(
        f"https://api.eia.gov/v2/seriesid/{series_id}",
        params={"api_key": KEY},
        timeout=30,
        headers=UA,
    )
    data = r.json().get("response", {}).get("data", [])
    df = pd.DataFrame(data)
    if df.empty:
        return df
    df["period"] = pd.to_datetime(df["period"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    return df.set_index("period").sort_index()


def main():
    confirm_key("EIA_API_KEY", KEY)
    summary = {}
    for sid, label in SERIES.items():
        try:
            df = eia_series(sid)
            df.to_parquet(OUT / f"{sid}.parquet")
            tail = df[["value", "units"]].tail(5) if not df.empty else df
            print(f"\n{sid} — {label}: rows={len(df)}")
            if not df.empty:
                print(tail.to_string())
                latest_date = df.index.max()
                latest_val = df.loc[latest_date, "value"]
                latest_units = df.loc[latest_date, "units"] if "units" in df.columns else "?"
                summary[sid] = {
                    "rows": int(len(df)),
                    "latest_period": str(latest_date.date()),
                    "latest_value": float(latest_val) if pd.notna(latest_val) else None,
                    "units": str(latest_units),
                    "label": label,
                }
        except Exception as e:
            print(f"{sid} fetch failed: {type(e).__name__}: {str(e)[:200]}")
            summary[sid] = {"error": f"{type(e).__name__}: {str(e)[:200]}", "label": label}

    summary["accessed_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, default=str))
    print(f"\nsummary.json saved")


if __name__ == "__main__":
    main()
