"""Probe Comtrade reporter codes for EU27 — 918 returned 0 rows, try alternatives."""
from __future__ import annotations
import os
import sys
from pathlib import Path

import httpx
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent))
from _safe import safe_get  # noqa: E402

load_dotenv(Path(__file__).resolve().parents[2] / ".env")
KEY = os.environ["COMTRADE_KEY"]
UA = {"User-Agent": "strategic-analyst/0.1"}


def probe(reporter: str, year: str = "2022") -> None:
    url = "https://comtradeapi.un.org/data/v1/get/C/A/HS"
    params = {
        "reporterCode": reporter,
        "partnerCode": "643",
        "period": year,
        "cmdCode": "27",
        "flowCode": "M",
        "subscription-key": KEY,
    }
    try:
        r = safe_get(url, params=params, timeout=60, headers=UA)
        data = r.json().get("data", [])
        print(f"reporter={reporter} year={year}: rows={len(data)}")
        if data:
            row = data[0]
            print(f"  reporterDesc={row.get('reporterDesc')} partnerDesc={row.get('partnerDesc')}")
            print(f"  primaryValue={row.get('primaryValue')} cmdCode={row.get('cmdCode')}")
    except Exception as e:
        print(f"reporter={reporter}: {type(e).__name__}: {str(e)[:200]}")


# 918 = EU27 (post-Brexit) per some docs; 97 = EU28 per old docs; 276 = Germany; 0 = world
for r in ["918", "97", "0", "276", "528", "250"]:
    probe(r, "2022")

# Also try aggregate "all" partners for Germany 2022 to confirm endpoint works
print("\nSanity: Germany 2022 from all partners, HS 27:")
url = "https://comtradeapi.un.org/data/v1/get/C/A/HS"
params = {
    "reporterCode": "276", "partnerCode": "0", "period": "2022",
    "cmdCode": "27", "flowCode": "M", "subscription-key": KEY,
}
r = safe_get(url, params=params, timeout=60, headers=UA)
data = r.json().get("data", [])
print(f"rows={len(data)}")
if data:
    print(f"  example: {data[0].get('reporterDesc')} <- {data[0].get('partnerDesc')} val={data[0].get('primaryValue'):,.0f}" )
