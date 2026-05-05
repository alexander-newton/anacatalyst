---
name: fetching-eia-energy
description: Use when the analyst needs US energy production, consumption, prices, inventories, refinery throughput, electric-grid generation, or imports/exports — daily, weekly, or monthly. Triggers include "what's WTI doing", "Cushing inventories", "natural-gas storage", "refinery utilisation", "power-grid mix", "EIA-914", any question about US energy data at series-level resolution.
---

# Fetching US Energy Data via EIA

## Overview

EIA (US Energy Information Administration, `eia.gov`) is the canonical source for US energy statistics — petroleum, natural gas, electricity, coal, nuclear, renewables — at a granularity (state, refinery, pipeline, generator) most countries don't publish. The API is free, well-organised, and updated to release schedule. For the analyst, EIA is the first stop on any US-energy question, and the cross-check on global flows where US data is the cleanest.

**Core principle:** *Cite the EIA series ID, not the article that quoted the number.* Like FRED, EIA's value is the series ID — reproducible, citable, and free of the framing layer that journalism adds.

## When to Use

- Pulling US oil / gas / electricity / coal time series at API granularity.
- Cross-checking a media claim about a US energy figure (DOE strategic-petroleum-reserve releases, refinery utilisation, storage levels).
- Building base rates ("how often has Cushing fallen below 25mb").
- Tracking weekly EIA reports (Wednesday weekly petroleum report, Thursday natural-gas storage) as a market signal.

**Skip for:**
- Non-US energy data — EIA has international tables, but the underlying source is usually JODI / IEA / national stats. Go upstream.
- Real-time prices — EIA publishes daily/weekly, not tick.
- Forecasts other than EIA's own STEO/AEO — for forecast comparison, IEA and OPEC publish theirs separately.

## API Setup

Free key, instant approval at [eia.gov/opendata/register.php](https://eia.gov/opendata/register.php). Set in `.env`:

```
EIA_API_KEY=...
```

**Endpoint:** `https://api.eia.gov/v2/`

The v2 API is hierarchical: navigate `/series/<route>/data/?api_key=...&data[]=value&facets[xxx][]=...`. Routes correspond to data products (petroleum, natural-gas, electricity, coal, nuclear, renewables, total-energy, international).

## The Two Patterns

### A. Series API — when you know the series ID

```python
import os, httpx, pandas as pd
KEY = os.environ["EIA_API_KEY"]

def eia_series(series_id: str) -> pd.DataFrame:
    """v1-style series ID, e.g. 'PET.RWTC.D' (WTI daily)."""
    r = httpx.get(f"https://api.eia.gov/v2/seriesid/{series_id}",
                  params={"api_key": KEY},
                  timeout=30,
                  headers={"User-Agent": "strategic-analyst/0.1"})
    r.raise_for_status()
    data = r.json().get("response", {}).get("data", [])
    df = pd.DataFrame(data)
    if not df.empty:
        df["period"] = pd.to_datetime(df["period"])
        df = df.set_index("period").sort_index()
    return df
```

### B. Route API — when you know the data product but want to discover series

```python
def eia_browse(route: str, **facets) -> dict:
    """Browse a data product, e.g. route='petroleum/pri/spt'.

    Note: facets are repeated query keys (facets[product][]=...&facets[product][]=...).
    httpx serialises repeated keys correctly when params is a list of (key, value)
    tuples — but NOT when params is a dict-of-list-values. Use the list-of-tuples form.
    """
    params: list[tuple[str, str]] = [("api_key", KEY)]
    for k, vs in facets.items():
        for v in vs:
            params.append((f"facets[{k}][]", v))
    r = httpx.get(f"https://api.eia.gov/v2/{route}/data/",
                  params=params, timeout=30,
                  headers={"User-Agent": "strategic-analyst/0.1"})
    r.raise_for_status()
    return r.json()
```

## Series IDs Worth Memorising

A small set covers most analyst questions. Use the v1-style ID with the `/seriesid/` path or the route-API equivalent.

| Topic | Series ID | Notes |
|---|---|---|
| **WTI Cushing daily** | `PET.RWTC.D` | The reference US oil price |
| **Brent (FOB) daily** | `PET.RBRTE.D` | Reference international price |
| **Natural gas Henry Hub daily** | `NG.RNGWHHD.D` | Reference US gas price |
| **Cushing crude inventory weekly** | `PET.W_EPC0_SAX_YCUOK_MBBL.W` | Watched closely by markets |
| **US crude inventory ex-SPR weekly** | `PET.WCESTUS1.W` | Total commercial stocks |
| **Strategic Petroleum Reserve weekly** | `PET.WCSSTUS1.W` | SPR level |
| **US crude production weekly** | `PET.WCRFPUS2.W` | EIA-914 weekly survey |
| **US crude production monthly** | `PET.MCRFPUS2.M` | More accurate monthly |
| **US refinery utilisation weekly** | `PET.WPULEUS3.W` | Refinery throughput as % of capacity |
| **Natural gas storage weekly** | `NG.NW2_EPG0_SWO_R48_BCF.W` | Lower 48 working gas; Thursday release |
| **Net electricity generation monthly** | `ELEC.GEN.ALL-US-99.M` | Total US, all sources |
| **Wind generation monthly** | `ELEC.GEN.WND-US-99.M` | |
| **Solar generation monthly** | `ELEC.GEN.SUN-US-99.M` | Utility-scale + small-scale |
| **Total US energy consumption** | `TOTAL.TETCBUS.A` | Annual quad-BTU |

For anything else, browse the catalogue at `https://www.eia.gov/opendata/browser/`.

## Worked Example — Cushing inventory and WTI together, last 2 years

```python
wti = eia_series("PET.RWTC.D")
cushing = eia_series("PET.W_EPC0_SAX_YCUOK_MBBL.W")
# Align on weekly basis for cross-comparison
weekly = wti.resample("W").last().join(cushing, rsuffix="_cushing", how="inner")
```

## Response Schema (what the API actually returns)

`/seriesid/<id>` returns a flat list of observations. Each row has these columns (verified 2026-05 against PET.RWTC.D and PET.W_EPC0_SAX_YCUOK_MBBL.W):

| Column | Type | Notes |
|---|---|---|
| `period` | str → datetime (set as index) | Daily / weekly / monthly per series |
| `duoarea` | str | Geography code (e.g. `YCUOK` = Cushing OK) |
| `area-name` | str | Often blank or `NA`; `duoarea` is the canonical key |
| `product` | str | EIA product code (e.g. `EPC0` = crude oil; `EPCWTIC` = WTI) |
| `product-name` | str | Human-readable product |
| `process` | str | Operation code (e.g. `SAX` = stocks; `PRI` = price) |
| `process-name` | str | Human-readable process |
| `series` | str | Full series ID this row belongs to |
| `series-description` | str | Human-readable description |
| `value` | float | The number |
| `units` | str | **Read this carefully** — see units note below |

**Units convention:** EIA reports many quantities in **thousand-units**. Inventory series typically come back as `MBBL` = thousand barrels (so a value of `29772` for Cushing inventory means ~29.8 *million* barrels, not 29 thousand). Price series come back as `$/BBL` or `$/MMBTU`. Always read the `units` column before interpreting the value — the same numeric scale means very different things across series.

## The Release Calendar — a Trading-Day Discipline

Several EIA releases are *market-moving*; their times matter:

| Release | When |
|---|---|
| Weekly Petroleum Status Report | Wednesday 10:30 ET (or Thursday after a Monday holiday) |
| Weekly Natural Gas Storage | Thursday 10:30 ET |
| Monthly STEO (Short-Term Energy Outlook) | Around the 7th of each month |
| Monthly Petroleum Supply Monthly | ~60-day lag, around the 1st |
| Annual Energy Outlook | Once per year, typically Q1 |

Caching the weekly series and refreshing 30 minutes after the scheduled release time avoids both stale data and unnecessary calls.

## Common Mistakes

| Mistake | Fix |
|---|---|
| Quoting weekly EIA-914 as if it were ground truth | EIA-914 is a survey-based estimate revised monthly. Use the monthly series for backward-looking analysis. |
| Treating SPR releases as reductions in commercial inventory | They're separate stocks; SPR draws *can* go to commercial market but the timing and cost basis differ. |
| Comparing nominal energy prices over decades without deflating | WTI in 2008 dollars and 2024 dollars are different things. Use a deflator. |
| Confusing crude with petroleum products | "US oil inventories" can mean crude only, total petroleum, or commercial-only. Be specific. |
| Reading STEO forecasts as ground truth | STEO is EIA's own near-term forecast. It is *one* forecast, not data. |
| Hard-coded series IDs that get deprecated | EIA renames series occasionally on schema changes. Cache the series-ID-to-current-name mapping. |
| Failing to set User-Agent | EIA logs UA and may rate-limit anonymous bulk callers. Identify the client. |

## Caching Pattern

EIA is append-only for most series — historical observations don't change, only new ones get added. Cache aggressively, refresh around release dates:

```python
import pathlib, time
CACHE = pathlib.Path("cache/eia"); CACHE.mkdir(parents=True, exist_ok=True)

def cached_eia(series_id: str, max_age_hours: int = 6) -> pd.DataFrame:
    path = CACHE / f"{series_id}.parquet"
    if path.exists() and (time.time() - path.stat().st_mtime) / 3600 < max_age_hours:
        return pd.read_parquet(path)
    df = eia_series(series_id)
    df.to_parquet(path)
    return df
```

Around weekly Wednesday/Thursday releases, drop `max_age_hours` to 0.5 so the cache refreshes immediately after the release window.

## Cross-References

- **REQUIRED: Apply `handling-credentials-safely`.** EIA takes the API key as a query string parameter, so URL-bearing exceptions leak it. Wrap calls in the documented `safe_get` redaction pattern; never echo `EIA_API_KEY` or full URLs in summaries.
- Output feeds `building-evidence-ledger`. Cite EIA series IDs with `accessed_at`; record the release date for weekly series, since revisions happen.
- For non-US data, prefer JODI / IEA / national stats, then cross-check the US-import side via EIA.
- The `analysing-economic-lens` and `analysing-geographic-lens` reach for energy data when the question turns on commodity prices or chokepoint flows.
- For commodity-pricing benchmarks beyond WTI/Brent/Henry Hub, see Platts / Argus (paid; see `data-sources.md`).
