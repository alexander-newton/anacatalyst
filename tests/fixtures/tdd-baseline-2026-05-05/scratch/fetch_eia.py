"""Pull WTI / Brent / US crude inventory / refinery utilisation from EIA.

Per skills/fetching-eia-energy/SKILL.md and skills/handling-credentials-safely/SKILL.md.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pandas as pd

from _safe import assert_key, safe_get

OUT = Path(__file__).resolve().parent.parent.parent / "cache" / "eia"
OUT.mkdir(parents=True, exist_ok=True)
HEADERS = {"User-Agent": "strategic-analyst/0.1 integration-test"}


def eia_series(series_id: str) -> pd.DataFrame:
    key = assert_key("EIA_API_KEY")
    r = safe_get(
        f"https://api.eia.gov/v2/seriesid/{series_id}",
        params={"api_key": key},
        timeout=30,
        headers=HEADERS,
    )
    data = r.json().get("response", {}).get("data", [])
    df = pd.DataFrame(data)
    if not df.empty:
        df["period"] = pd.to_datetime(df["period"])
        df = df.set_index("period").sort_index()
    return df


SERIES = {
    "wti_daily": "PET.RWTC.D",
    "brent_daily": "PET.RBRTE.D",
    "us_crude_inventory_weekly_ex_spr": "PET.WCESTUS1.W",
    "refinery_utilisation_weekly": "PET.WPULEUS3.W",
    "spr_weekly": "PET.WCSSTUS1.W",
}


def main() -> int:
    for label, sid in SERIES.items():
        try:
            df = eia_series(sid)
            df.to_parquet(OUT / f"{label}.parquet")
            if not df.empty and "value" in df.columns:
                last_date = df.index[-1].date()
                last_val = df["value"].dropna().iloc[-1]
                units = df["units"].iloc[-1] if "units" in df.columns else ""
                print(f"[eia] {label:35s} ({sid:35s}) last={last_date} value={last_val} {units}",
                      file=sys.stderr)
            else:
                print(f"[eia] {label} returned empty frame", file=sys.stderr)
        except Exception as e:
            print(f"[eia] {label} errored: {type(e).__name__}: {e}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
