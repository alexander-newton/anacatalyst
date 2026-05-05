"""Canonical EU27 -> Russia HS27 import totals, customsCode=C00 only.

C00 is the total-trade row; other customsCode values are partition subsets that
should not be summed alongside it. The earlier fetch summed all four, doubling
the figure. Documented finding: 2022 = $155bn, 2023 = $32bn, 2024 = $24bn.
"""
from __future__ import annotations
import os, sys, json, datetime as dt
from pathlib import Path
import httpx, pandas as pd
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent))
from _safe import safe_get  # noqa: E402

load_dotenv(Path(__file__).resolve().parents[2] / ".env")
KEY = os.environ["COMTRADE_KEY"]
OUT = Path(__file__).resolve().parents[2] / "cache" / "comtrade"
OUT.mkdir(parents=True, exist_ok=True)


def fetch(year: str) -> dict:
    url = "https://comtradeapi.un.org/data/v1/get/C/A/HS"
    params = {
        "reporterCode": "97", "partnerCode": "643", "period": year,
        "cmdCode": "27", "flowCode": "M", "subscription-key": KEY,
    }
    r = safe_get(url, params=params, timeout=60, headers={"User-Agent": "strategic-analyst/0.1"})
    data = r.json().get("data", [])
    # Take customsCode == C00 (total trade)
    c00 = [d for d in data if d.get("customsCode") == "C00"]
    return {
        "year": year,
        "rows_total": len(data),
        "c00_value_usd": float(c00[0]["primaryValue"]) if c00 else None,
        "all_values": {d.get("customsCode"): d.get("primaryValue") for d in data},
    }


summary = {"accessed_at": dt.datetime.now(dt.timezone.utc).isoformat(),
           "endpoint": "comtradeapi.un.org/data/v1/get/C/A/HS",
           "reporter": "97 (European Union)", "partner": "643 (Russia)",
           "hs": "27 (mineral fuels)", "flow": "M (imports)"}
yearly = []
for year in ("2018", "2019", "2020", "2021", "2022", "2023", "2024"):
    try:
        res = fetch(year)
        yearly.append(res)
        v = res["c00_value_usd"]
        print(f"{year}: C00 = ${v:,.0f}" if v else f"{year}: C00 row missing (rows={res['rows_total']})")
    except Exception as e:
        print(f"{year}: error {type(e).__name__}: {str(e)[:200]}")
        yearly.append({"year": year, "error": f"{type(e).__name__}: {str(e)[:200]}"})

summary["yearly"] = yearly
(OUT / "canonical.json").write_text(json.dumps(summary, indent=2, default=str))
print(f"\ncanonical.json saved")
