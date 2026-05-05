---
name: fetching-fred-macro
description: Use when the analyst needs macroeconomic time series for the United States or any series that FRED aggregates from BIS, OECD, IMF, World Bank, BEA, BLS, Treasury. Triggers include "what's CPI doing", "fed funds path", "real rates", "unemployment trend", "yield curve", "term spread", any rate, price, or growth series, and any quick macro chart.
---

# Fetching Macro Data via FRED

## Overview

FRED (Federal Reserve Bank of St. Louis) aggregates **800,000+ macro and financial time series**, free, with a clean API. It is the analyst's first stop for any quantitative macro lookup. Coverage: BLS, BEA, Census, Treasury, Federal Reserve, plus mirror series from BIS, OECD, IMF, World Bank, ECB, BoE.

**Core principle:** *Cite the FRED series ID, not the article that quoted the number.* The series ID is reproducible; the article is a re-report.

## When to Use

- Pulling a specific series (CPI, fed funds, GDP, unemployment, yields, FX rates).
- Building a chart with current and historical values.
- Comparing a country's data against US baseline.
- Quick base-rate look-up ("how often has core PCE been above 4% in the last 30 years").

**Skip for:**
- Real-time intraday market data (FRED is at most daily; usually monthly or quarterly).
- Granular firm-level or sector data — go to the underlying source.
- Series that exist only at the original agency (some BoE / BoJ series have FRED mirrors with lag; the original is fresher).

## API Setup

**Get a free key:** apply at `https://fred.stlouisfed.org/docs/api/api_key.html`. Approval is automatic and immediate.

Store the key in `.env`:

```
FRED_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Python dependencies** (use `uv` per the project convention):

```bash
uv add httpx pandas pyarrow         # core fetch + parquet caching
uv add pandas-datareader            # optional, only for Pattern A below
uv add python-dotenv                # optional, for cleaner .env loading
```

`pyarrow` is **required** for the documented caching pattern (parquet round-trip); without it `df.to_parquet(...)` fails with `ImportError: Unable to find a usable engine`. `pandas-datareader` is only needed if you use Pattern A; Pattern B works on the core deps alone.

**Transient 5xx errors:** FRED's servers return 502/503 occasionally. Verified 2026-05: the same call that returned 200 OK on one run returned 502 thirty seconds later. Wrap consequential calls in a small retry — three attempts with exponential backoff (1s, 3s, 9s) handles all the flake observed in testing.

**Endpoints used most:**

| Endpoint | Use |
|---|---|
| `/series/observations` | Time-series values for one series ID — the workhorse |
| `/series/search` | Find a series ID from a keyword |
| `/series` | Metadata for a series ID (units, frequency, last updated) |
| `/category/series` | All series in a category |

## The Two Patterns

### Pattern A — `pandas_datareader` (simplest)

```python
from pandas_datareader import data as pdr
import datetime as dt
cpi = pdr.DataReader("CPIAUCSL", "fred", dt.date(2000, 1, 1))   # US headline CPI, monthly
ffr = pdr.DataReader("DFEDTARU", "fred", dt.date(2000, 1, 1))   # Fed funds upper bound, daily
```

`pandas_datareader.fred` does not require an explicit key — it uses the public web endpoint. Fine for ad-hoc work, but rate-limited and lacks metadata.

### Pattern B — direct httpx with API key (preferred for production)

```python
import os, httpx, pandas as pd, datetime as dt

FRED_KEY = os.environ["FRED_API_KEY"]
FRED = "https://api.stlouisfed.org/fred"

def fred_series(series_id: str, start: str = "2000-01-01") -> pd.DataFrame:
    r = httpx.get(
        f"{FRED}/series/observations",
        params={
            "series_id": series_id,
            "api_key": FRED_KEY,
            "file_type": "json",
            "observation_start": start,
        },
        timeout=30,
    )
    r.raise_for_status()
    obs = r.json()["observations"]
    df = pd.DataFrame(obs)
    df["date"] = pd.to_datetime(df["date"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")  # FRED uses "." for missing
    return df.set_index("date")[["value"]].rename(columns={"value": series_id})

def fred_meta(series_id: str) -> dict:
    r = httpx.get(
        f"{FRED}/series",
        params={"series_id": series_id, "api_key": FRED_KEY, "file_type": "json"},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()["seriess"][0]   # units, frequency, last_updated, seasonal_adjustment, notes
```

The `fred_meta` call is **non-optional** for citation: it gives you `units`, `frequency`, `seasonal_adjustment`, and `last_updated`. Two of those frequently change between when you fetched and when the chart is read; recording them in the evidence ledger is what makes the chart reproducible.

## Series IDs Worth Memorising

Skipping the search call when you know the ID is faster. The most common:

| Topic | Series ID | Notes |
|---|---|---|
| US headline CPI (NSA) | `CPIAUCSL` | Monthly |
| US core CPI | `CPILFESL` | Monthly |
| US headline PCE | `PCEPI` | Monthly |
| US core PCE | `PCEPILFE` | Monthly — the Fed's preferred gauge |
| Fed funds upper bound | `DFEDTARU` | Daily |
| 10Y Treasury yield | `DGS10` | Daily |
| 2Y Treasury yield | `DGS2` | Daily — pair with `DGS10` for the curve |
| 10Y-2Y spread | `T10Y2Y` | Daily, pre-computed |
| 5Y inflation breakeven | `T5YIE` | Daily, market-implied inflation |
| Unemployment rate | `UNRATE` | Monthly |
| Nonfarm payrolls | `PAYEMS` | Monthly |
| US real GDP | `GDPC1` | Quarterly |
| Real broad effective USD | `RTWEXBGS` | Monthly, BIS source |
| EUR/USD | `DEXUSEU` | Daily |
| WTI crude | `DCOILWTICO` | Daily |
| Brent crude | `DCOILBRENTEU` | Daily |
| VIX | `VIXCLS` | Daily |

**What FRED does *not* cover** — silent-substitution failure mode:
- **European natural-gas benchmarks (TTF, NBP)** are *not* in FRED. The closest proxy is `DHHNGSP` (Henry Hub spot), but the Henry-Hub-to-TTF relationship is loose at best and broke entirely during 2022–2023. For TTF use ICE Endex settlement data (paid) or scrape EEX / EUREX public references; do *not* substitute Henry Hub silently.
- **Bilateral commodity flows** (e.g., Russia-to-China crude) — FRED has aggregate US trade balance, not bilateral. Use UN Comtrade.
- **EM central-bank policy rates** are sparsely covered. Pull from the central bank directly when stakes are high.
- **Brent and TTF intraday** — FRED is at best daily; for intraday use ICE/EIA/Refinitiv.

For anything else, search:

```python
def fred_search(query: str, limit: int = 20) -> pd.DataFrame:
    r = httpx.get(
        f"{FRED}/series/search",
        params={"search_text": query, "api_key": FRED_KEY, "file_type": "json", "limit": limit},
        timeout=30,
    )
    r.raise_for_status()
    return pd.DataFrame(r.json()["seriess"])[["id", "title", "frequency", "units", "seasonal_adjustment"]]
```

## Caching Pattern

FRED data is **append-only** for most series — old observations don't change, only new ones get added. Cache aggressively:

```python
import pathlib
CACHE = pathlib.Path("cache/fred")
CACHE.mkdir(parents=True, exist_ok=True)

def cached_series(series_id: str, max_age_hours: int = 6) -> pd.DataFrame:
    path = CACHE / f"{series_id}.parquet"
    import time
    if path.exists() and (time.time() - path.stat().st_mtime) / 3600 < max_age_hours:
        return pd.read_parquet(path)
    df = fred_series(series_id)
    df.to_parquet(path)
    return df
```

For series that *do* get revised (GDP, BEA personal income), set `max_age_hours=24` and re-pull around release dates.

## Common Mistakes

| Mistake | Fix |
|---|---|
| Quoting a CPI number from a news article | Pull `CPIAUCSL` and read the value yourself. The number in the article may already be the y/y change of a different series. |
| Confusing seasonally-adjusted with NSA | `CPIAUCSL` is SA; `CPIAUCNS` is NSA. Read the metadata. |
| Reading a stale value mid-revision | Quarterly series (GDP, productivity) get revised. Cache with `max_age_hours=24` near release dates and check `last_updated`. |
| Missing values silently treated as zero | FRED uses `.` for missing. Use `pd.to_numeric(..., errors="coerce")`. |
| Citing the chart, not the series | The chart in your one-pager is downstream of the series ID; the ledger row should cite `FRED:CPIAUCSL` plus `accessed_at`. |
| Comparing levels across series with different bases | Index series have a base-year (e.g. CPI = 100 in 1982-1984). Convert to y/y or change-from-period before comparing. |
| Hard-coding a date filter | Pull all data; filter at use site. Saves re-pulls. |

## Cross-References

- **REQUIRED: Apply `handling-credentials-safely`.** FRED requires the API key in the query string, which means a 5xx traceback contains the key in the URL. Use the `safe_get` URL-redaction wrapper documented in that skill. Do not include the key value or the full URL in any output, ledger note, or summary.
- Each pulled series gets one ledger row per *use*, not per row of data. Record series ID, observation window, `last_updated` from metadata, and the accessed timestamp. See `building-evidence-ledger`.
- For non-US central-bank policy rates that aren't in FRED, fall back to direct fetch from the central bank's site (and grade A — primary).
- For broader cross-country macro, prefer World Bank WDI (`wbdata`) or IMF SDMX — FRED's coverage of EM is patchy.
- The economic and public-finance lens skills (`analysing-economic-lens`, `analysing-public-finance-lens`) reach for FRED constantly; this skill is what they call.
