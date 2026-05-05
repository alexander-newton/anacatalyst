"""Inspect the 4-row structure for reporter=97 to understand the doubling."""
from __future__ import annotations
import os, sys, json
from pathlib import Path
import httpx
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent))
from _safe import safe_get  # noqa: E402

load_dotenv(Path(__file__).resolve().parents[2] / ".env")
KEY = os.environ["COMTRADE_KEY"]

url = "https://comtradeapi.un.org/data/v1/get/C/A/HS"
params = {
    "reporterCode": "97", "partnerCode": "643", "period": "2022",
    "cmdCode": "27", "flowCode": "M", "subscription-key": KEY,
}
r = safe_get(url, params=params, timeout=60, headers={"User-Agent": "strategic-analyst/0.1"})
data = r.json().get("data", [])
print(f"rows={len(data)}")
for i, row in enumerate(data):
    nonempty = {k: v for k, v in row.items() if v not in (None, 0, 0.0, "", "0")}
    print(f"--- row {i} ---")
    for k, v in nonempty.items():
        print(f"  {k}: {v}")
