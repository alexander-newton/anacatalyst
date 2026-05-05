"""Pull EU (reporter=918, EU27 aggregate) imports of HS 27 (mineral fuels) from
Russia (partner=643), 2022–2024 annual.

Note on reporter codes: EU27 in M49 is 918 (post-2020 composition). If 918
returns empty, fall back to the union of the major member states (Germany 276,
France 250, Italy 380, Spain 724, Netherlands 528, Poland 616, ...).

Per skills/fetching-comtrade-trade/SKILL.md and skills/handling-credentials-safely/SKILL.md.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import pandas as pd

from _safe import assert_key, safe_get

OUT = Path(__file__).resolve().parent.parent.parent / "cache" / "comtrade"
OUT.mkdir(parents=True, exist_ok=True)
HEADERS = {"User-Agent": "strategic-analyst/0.1 integration-test"}


def comtrade_get(reporter: str, partner: str, period: str, hs: str = "27",
                 flow: str = "M") -> pd.DataFrame:
    key = assert_key("COMTRADE_KEY")
    url = "https://comtradeapi.un.org/data/v1/get/C/A/HS"
    params = {
        "reporterCode": reporter,
        "partnerCode": partner,
        "period": period,
        "cmdCode": hs,
        "flowCode": flow,
        "subscription-key": key,
    }
    r = safe_get(url, params=params, timeout=60, headers=HEADERS)
    return pd.DataFrame(r.json().get("data", []))


def main() -> int:
    rows = []
    # EU27 aggregate (M49 918), HS 27 imports from Russia (643), 2022-2024
    for year in ("2022", "2023", "2024"):
        try:
            df = comtrade_get("918", "643", year, "27", "M")
            print(f"[comtrade] EU27<-RUS HS27 {year}: {len(df)} rows", file=sys.stderr)
            if not df.empty and "primaryValue" in df.columns:
                total_usd = df["primaryValue"].sum()
                print(f"[comtrade]   total CIF value: ${total_usd:,.0f}", file=sys.stderr)
                rows.append({"year": year, "rows": len(df), "value_usd": total_usd})
            df.to_parquet(OUT / f"eu27_rus_hs27_{year}.parquet")
            time.sleep(1)
        except Exception as e:
            print(f"[comtrade] {year} errored: {type(e).__name__}: {e}", file=sys.stderr)
    summary = pd.DataFrame(rows)
    summary.to_csv(OUT / "summary.csv", index=False)
    print(f"\n[comtrade] summary:\n{summary.to_string()}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
