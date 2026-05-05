"""Fetch UN Comtrade — EU27 (reporter=918) imports of HS27 from Russia (partner=643), 2022-2024 annual.

Documented in skills/fetching-comtrade-trade/SKILL.md.
"""
from __future__ import annotations
import os
import sys
import json
import datetime as dt
import time
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent))
from _safe import safe_get, confirm_key  # noqa: E402

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

OUT = Path(__file__).resolve().parents[2] / "cache" / "comtrade"
OUT.mkdir(parents=True, exist_ok=True)

KEY = os.environ["COMTRADE_KEY"]
UA = {"User-Agent": "strategic-analyst/0.1 (test)"}


def comtrade_get(reporter: str, partner: str, period: str, hs: str, flow: str = "M") -> pd.DataFrame:
    url = "https://comtradeapi.un.org/data/v1/get/C/A/HS"
    params = {
        "reporterCode": reporter,
        "partnerCode": partner,
        "period": period,
        "cmdCode": hs,
        "flowCode": flow,
        "subscription-key": KEY,
    }
    r = safe_get(url, params=params, timeout=60, headers=UA)
    payload = r.json()
    return pd.DataFrame(payload.get("data", []))


def main():
    confirm_key("COMTRADE_KEY", KEY)
    # NB: 918 returns 0 rows from this endpoint (probed). 97 = "European Union"
    # (the reporter Comtrade exposes for EU aggregate) returns the right values.
    EU27 = "97"
    RUSSIA = "643"
    HS = "27"  # mineral fuels chapter
    summary = {"accessed_at": dt.datetime.now(dt.timezone.utc).isoformat()}

    rows = []
    for year in ("2021", "2022", "2023", "2024"):
        try:
            df = comtrade_get(EU27, RUSSIA, year, HS, "M")
            df.to_parquet(OUT / f"eu27_imp_hs27_rus_{year}.parquet")
            print(f"\nEU27 imports HS27 from RU, year={year}: rows={len(df)}")
            if not df.empty:
                cols = [c for c in ("period", "reporterDesc", "partnerDesc", "cmdCode", "cmdDesc",
                                    "flowDesc", "primaryValue", "netWgt", "qty") if c in df.columns]
                preview = df[cols].head(3).to_string()
                print(preview)
                total_value = df["primaryValue"].sum() if "primaryValue" in df.columns else None
                rows.append({
                    "year": year,
                    "rows": int(len(df)),
                    "primary_value_usd_total": float(total_value) if total_value is not None else None,
                })
            else:
                rows.append({"year": year, "rows": 0, "primary_value_usd_total": None})
        except Exception as e:
            print(f"comtrade fetch failed for {year}: {type(e).__name__}: {str(e)[:200]}")
            rows.append({"year": year, "error": f"{type(e).__name__}: {str(e)[:200]}"})
        time.sleep(1)  # polite

    summary["yearly"] = rows
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, default=str))
    print(f"\nsummary.json saved")
    for r in rows:
        if r.get("primary_value_usd_total") is not None:
            print(f"  {r['year']}: ${r['primary_value_usd_total']:,.0f}")


if __name__ == "__main__":
    main()
