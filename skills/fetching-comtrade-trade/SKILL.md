---
name: fetching-comtrade-trade
description: Use when the analyst needs bilateral merchandise trade data — flows between two countries, by HS commodity code, by month or year. Triggers include "how much does X import from Y", "trade exposure to Z", "tariff schedule", "supply chain dependency", "export concentration", "import-substitution", any question about a specific commodity's bilateral or global flows.
---

# Fetching Bilateral Trade via UN Comtrade

## Overview

UN Comtrade (`comtradeplus.un.org`) is the canonical global merchandise-trade database — bilateral flows between every pair of reporting economies, by HS commodity code, monthly and annual back to the 1960s. Trade data is the most reliable economic dataset most countries publish, because customs has independent revenue-collection incentives. The analyst uses Comtrade for any "who depends on whom" question.

**Core principle:** *Bilateral trade has two reports — exporter and importer — and they rarely match.* Pulling both and reconciling is the methodology. Choosing one without saying which is sloppy.

## When to Use

- Quantifying a country's exposure to / dependence on another (energy, food, semiconductors, defence).
- Checking whether a sanctions or tariff regime has actually shifted flows.
- Validating a claim about a specific commodity's trade trajectory.
- Building base rates for "X is Y's largest supplier" (often misstated — verify).

**Skip for:**
- Services trade (Comtrade is merchandise only — use IMF BPM6 / OECD TIVA / national statistics for services).
- Real-time trade — Comtrade lags 60–180 days for monthly data.
- Goods that move outside the customs system (illicit flows, very small e-commerce).

## API Setup

Register at [comtradeplus.un.org](https://comtradeplus.un.org/api/Subscription) for a free API key. The free tier permits ~250 requests/day; bulk extraction needs a paid subscription.

```
COMTRADE_KEY=...
```

## Two Endpoints

### A. Get reported trade — the workhorse

```
GET https://comtradeapi.un.org/data/v1/get/{typeCode}/{freqCode}/{clCode}
```

Path params:
- `typeCode`: `C` (commodities) or `S` (services — limited).
- `freqCode`: `A` (annual) or `M` (monthly).
- `clCode`: HS classification version, typically `HS` (latest) or `HS22`, `HS17`, etc.

Query params (the useful ones):
- `reporterCode` — M49 country code or `all`.
- `partnerCode` — M49 country code or `all`.
- `period` — year `2024` or year-month `202403`.
- `cmdCode` — HS code at 2-, 4-, or 6-digit level (e.g., `27` = mineral fuels, `2710` = petroleum oils, `271019` = a specific type).
- `flowCode` — `M` (import), `X` (export), `RX` (re-export), `RM` (re-import).

Worked example — Germany's imports of natural gas (HS 2711) by partner, 2024 annual:

```python
import os, httpx, pandas as pd
KEY = os.environ["COMTRADE_KEY"]

def comtrade_get(reporterCode: str, partnerCode: str = "all",
                 period: str = "2024", cmdCode: str = "TOTAL",
                 flowCode: str = "M", freqCode: str = "A",
                 typeCode: str = "C", clCode: str = "HS",
                 customs_code: str = "C00") -> pd.DataFrame:
    """Fetch Comtrade data with the canonical-total customs filter applied.

    customs_code='C00' returns the total-trade row (recommended default).
    Setting customs_code=None returns all rows (C00, C01, C06, C20) — naive
    summing across these double-counts because C01/C06/C20 are subsets of C00.
    """
    url = f"https://comtradeapi.un.org/data/v1/get/{typeCode}/{freqCode}/{clCode}"
    params = {
        "reporterCode": reporterCode,
        "partnerCode": partnerCode,
        "period": period,
        "cmdCode": cmdCode,
        "flowCode": flowCode,
        "subscription-key": KEY,
    }
    r = httpx.get(url, params=params, timeout=30,
                  headers={"User-Agent": "strategic-analyst/0.1"})
    r.raise_for_status()
    df = pd.DataFrame(r.json().get("data", []))
    if customs_code and not df.empty and "customsCode" in df.columns:
        df = df[df["customsCode"] == customs_code].reset_index(drop=True)
    return df

# Germany (276) importing HS 2711 from all partners, 2024
df = comtrade_get("276", "all", "2024", "2711", "M")
```

**`customsCode` gotcha (verified 2026-05-05):** Each Comtrade query typically returns **four rows per (reporter, partner, commodity, period, flow) tuple** under different `customsCode` values: **`C00` is the total**, `C01` / `C06` / `C20` are subsets (specific customs procedures). Naive `df["primaryValue"].sum()` triple-counts. Always filter `customsCode == "C00"` for the canonical aggregate, or sum only one of the C01/C06/C20 categories if you need that specific procedure. The `comtrade_get` helper above does this filter by default.

### B. Reference data — country and commodity codes

Country codes are M49 (e.g., 276 = Germany, 156 = China, 840 = USA). Comtrade publishes the lookup at `https://comtradeapi.un.org/files/v1/app/reference/Reporters.json`. Cache it locally; it changes rarely.

**EU reporter-code gotcha (verified 2026-05-05):** Comtrade ships an EU27 entry at M49 code `918`, but the live `/data/v1/get/C/A/HS` endpoint returns **0 rows** for `reporter=918`. The working code for the EU as a single reporter is `97` ("European Union"). Use `97`; reserve `918` for documentation citations only.

Commodity codes follow Harmonised System (HS):
- 2-digit: chapter (`27` mineral fuels)
- 4-digit: heading (`2711` petroleum gases)
- 6-digit: subheading (`271121` natural gas, gaseous)
- 8/10-digit: country-specific extensions (not in Comtrade core)

The HS lookup is in the same `/files/v1/app/reference/` namespace.

## The Mirror-Statistics Problem

Bilateral trade has two reports — *exporter X says X→Y was $A; importer Y says X→Y was $B*. **They almost never agree.** Reasons:

- Different valuation bases (FOB at exporter, CIF at importer; CIF includes shipping/insurance, ~5–15% more).
- Re-exports counted as exports by intermediary, not by ultimate origin.
- Transhipment (e.g., goods routed through Singapore are often reported with Singapore as partner).
- Time-of-recording differences (when goods cross borders vs when documentation clears).
- Misreporting (every customs administration has incentives — revenue, balance-of-payments management, sanctions evasion).

**The methodology:**

1. Pull both legs (importer's reported imports from exporter; exporter's reported exports to importer).
2. State which one you're using and why.
3. If they diverge by >20%, that divergence is itself the story — *especially* for commodities where one side has reasons to misreport (e.g., Russia sanctions-era oil flows).

CEPII's BACI dataset (a separate skill, when written) reconciles bilateral flows for academic use; for live analysis, Comtrade with explicit mirror-statistics handling is the standard.

## Common Mistakes

| Mistake | Fix |
|---|---|
| Citing only one leg of bilateral trade | Pull both; compare; state the choice. |
| Using `M49` and `ISO-3` interchangeably | They are different. M49 is numeric (276); ISO-3 is alpha (DEU). The API takes M49. |
| HS-2 query when the question is HS-6 | "Mineral fuels" (HS 27) lumps oil, gas, coal, and electricity. Drill to HS-4 or HS-6. |
| Ignoring re-exports | A small "ultimate origin" can show up as a large flow via a transhipment hub. Decompose if precision matters. |
| Comparing values without deflating | Commodity-price swings move nominal trade more than volumes. Use volume columns where available, or deflate by HS-specific price index. |
| Caching Comtrade as if it were static | Recent quarters can be revised. Refresh the trailing 12 months on every run. |
| Treating "Singapore" as the buyer | Singapore is a transhipment economy. For oil and electronics in particular, ultimate origin/destination is often elsewhere. |
| Using HS-2017 codes after HS-2022 update | HS revisions change codes every 5 years. Match the version you're querying with `clCode`. |

## Caching Pattern

Annual data older than 18 months is effectively stable. Cache aggressively for that window; refresh recent quarters and the live year:

```python
import pathlib, time
CACHE = pathlib.Path("cache/comtrade"); CACHE.mkdir(parents=True, exist_ok=True)

def cached_comtrade(reporter: str, hs: str, year: str) -> pd.DataFrame:
    path = CACHE / f"{reporter}-{hs}-{year}.parquet"
    is_recent = (int(year) >= int(time.strftime("%Y")) - 1)
    if path.exists() and not is_recent:
        return pd.read_parquet(path)
    df = comtrade_get(reporter, "all", year, hs, "M")
    df.to_parquet(path)
    return df
```

## Cross-References

- **REQUIRED: Apply `handling-credentials-safely`.** Comtrade takes the subscription-key as a query string parameter; URL-bearing exceptions leak it. Use the documented `safe_get` redaction pattern.
- Output rows feed `building-evidence-ledger`. Cite Comtrade by `(reporter, partner, HS code, period, flow)`; record which leg of the bilateral was used.
- Use `fetching-fred-macro` or central-bank sources for trade balances at aggregate level.
- For tariff schedules (vs trade data), see WITS or USITC DataWeb (separate skills, when written).
- The `analysing-economic-lens` and `analysing-public-finance-lens` reach for trade data when the question turns on dependency or BOP composition.
