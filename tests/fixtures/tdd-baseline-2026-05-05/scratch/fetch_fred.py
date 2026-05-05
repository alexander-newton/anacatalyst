"""Pull EUR/USD, real broad effective USD, Brent, WTI proxies from FRED.

TTF (European gas) is not in FRED directly; we pull Henry Hub as a proxy and
note in the ledger.

Per skills/fetching-fred-macro/SKILL.md and skills/handling-credentials-safely/SKILL.md.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

from _safe import assert_key, safe_get

OUT = Path(__file__).resolve().parent.parent.parent / "cache" / "fred"
OUT.mkdir(parents=True, exist_ok=True)
HEADERS = {"User-Agent": "strategic-analyst/0.1 integration-test"}

SERIES = {
    "DEXUSEU": "USD/EUR daily",
    "RTWEXBGS": "Real broad effective USD",
    "DCOILBRENTEU": "Brent daily",
    "DCOILWTICO": "WTI daily",
    "DHHNGSP": "Henry Hub daily (TTF proxy)",
}


def fred_series(series_id: str) -> pd.DataFrame:
    key = assert_key("FRED_API_KEY")
    r = safe_get(
        "https://api.stlouisfed.org/fred/series/observations",
        params={
            "series_id": series_id,
            "api_key": key,
            "file_type": "json",
            "observation_start": "2022-01-01",
        },
        timeout=30,
        headers=HEADERS,
    )
    obs = r.json()["observations"]
    df = pd.DataFrame(obs)
    if df.empty:
        return df
    df["date"] = pd.to_datetime(df["date"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    return df.set_index("date")[["value"]].rename(columns={"value": series_id})


def main() -> int:
    for sid, label in SERIES.items():
        try:
            df = fred_series(sid)
            df.to_parquet(OUT / f"{sid}.parquet")
            if not df.empty:
                last = df.dropna().iloc[-1]
                print(f"[fred] {sid:15s} ({label:35s}) last={last.name.date()} = {float(last.iloc[0]):.4f}",
                      file=sys.stderr)
        except Exception as e:
            print(f"[fred] {sid} errored: {type(e).__name__}: {e}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
