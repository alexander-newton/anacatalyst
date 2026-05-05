---
name: fetching-acled-events
description: Use when the analyst needs coded conflict events — battles, protests, strategic developments, violence against civilians — by country, region, actor, or time window. Triggers include "what's the conflict tempo in X", "ACLED data on Y", "coup attempts", "civil-violence trend", "protest events", any case where a structured event database is needed instead of news prose.
---

# Fetching Conflict Events via ACLED

## Overview

ACLED (Armed Conflict Location & Event Data) is the standard structured database for coded conflict events worldwide — battles, explosions/remote violence, violence against civilians, riots, protests, strategic developments. Coverage is daily-updated for most regions, with named actors, lat/long, fatality estimates, and source links. It is the analyst's first stop for any "tempo of violence" or "actor footprint" question.

**Core principle:** *ACLED is structured journalism, not satellite truth.* Events are coded from open-source reporting; coding decisions matter. The analyst grades the *event*, not the database, and uses ACLED as a sampling frame against which other sources are checked.

## When to Use

- Quantifying conflict tempo by country, region, actor, or event type over a window.
- Finding *named actor* event histories (e.g., "all events involving Wagner Group in Mali, 2023–25").
- Building base rates ("how often do coups occur in West Africa per decade").
- Cross-checking a media claim about a battle / strike / massacre against the structured record.

**Skip for:**
- Real-time breaking events (ACLED has a 1–7 day lag depending on region; some regions longer).
- Events outside ACLED's coding criteria (e.g., low-level criminal violence, most cyber operations).
- Casualty totals as ground truth — ACLED's fatality figures are best-effort and conservative.

## API Setup

Register at [acleddata.com/data-export-tool/](https://acleddata.com/data-export-tool/). Approval is automatic on email confirmation. Set in `.env`:

```
ACLED_KEY=...
ACLED_EMAIL=you@example.com
```

The API requires both on every request — `email` is treated as part of the credential.

**Endpoint:** `https://api.acleddata.com/acled/read`

## The Workhorse Call

```python
import os, httpx, pandas as pd

ACLED_KEY = os.environ["ACLED_KEY"]
ACLED_EMAIL = os.environ["ACLED_EMAIL"]

def acled_events(country: str | None = None,
                 region: str | None = None,
                 event_type: str | None = None,
                 actor1: str | None = None,
                 event_date_start: str | None = None,
                 event_date_end: str | None = None,
                 limit: int = 5000) -> pd.DataFrame:
    """Fetch ACLED events with the most useful filters.

    Dates: YYYY-MM-DD. Use event_date_start..event_date_end (BETWEEN logic).
    Country: full English name (e.g., 'Sudan'). Pipe-separated for multiple.
    Region: 1=Western Africa, 2=Middle Africa, ... see ACLED docs.
    Event type: 'Battles' | 'Explosions/Remote violence' | 'Violence against civilians' |
                'Protests' | 'Riots' | 'Strategic developments'.
    """
    params = {
        "key": ACLED_KEY,
        "email": ACLED_EMAIL,
        "limit": limit,
    }
    if country:
        params["country"] = country
    if region:
        params["region"] = region
    if event_type:
        params["event_type"] = event_type
    if actor1:
        params["actor1"] = actor1
        params["actor1_where"] = "LIKE"  # substring match
    if event_date_start and event_date_end:
        params["event_date"] = f"{event_date_start}|{event_date_end}"
        params["event_date_where"] = "BETWEEN"
    r = httpx.get("https://api.acleddata.com/acled/read",
                  params=params, timeout=30,
                  headers={"User-Agent": "strategic-analyst/0.1"})
    r.raise_for_status()
    return pd.DataFrame(r.json().get("data", []))
```

Worked example — battles in Sudan in March 2026:

```python
df = acled_events(country="Sudan",
                  event_type="Battles",
                  event_date_start="2026-03-01",
                  event_date_end="2026-03-31")
```

## Schema (the columns worth knowing)

| Column | Type | Notes |
|---|---|---|
| `event_id_cnty` | str | Stable per-country event ID — use as the dedup key |
| `event_date` | str | YYYY-MM-DD |
| `event_type` | str | One of the six categories above |
| `sub_event_type` | str | Finer-grained — e.g., 'Armed clash', 'Air/drone strike' |
| `actor1`, `actor2` | str | Named actor (state, rebel group, ethnic militia, civilians) |
| `assoc_actor_1` | str | Associated entities (often where alliances are visible) |
| `inter1`, `inter2` | int | Actor-type code (1=state forces, 2=rebel group, 3=militia, etc.) |
| `country` / `admin1` / `admin2` / `location` | str | Place hierarchy |
| `latitude` / `longitude` | float | Point coordinates |
| `geo_precision` | int | 1–3 (1 = precise; 3 = country level only — be careful) |
| `fatalities` | int | **Conservative best-estimate**; treat as a lower bound |
| `notes` | str | Free-text describing the event; keep but don't quote uncritically |
| `source` / `source_scale` | str | Reporting source(s); scale 'Subnational' / 'National' / 'International' |

## Gradient Rules — How to Read ACLED

- **Source scale matters.** International-source events are typically better-corroborated; subnational-only events have higher coding-error rates.
- **`geo_precision = 3` rows place the event "somewhere in the country".** Useful for tempo, useless for spatial analysis.
- **Fatalities are conservative.** ACLED systematically undercounts in environments with restricted reporting. Rising fatalities-per-event is often a *reporting* signal, not a kinetic one.
- **Actor naming changes over time.** Reorganisations (e.g., Wagner → Africa Corps in 2024) require name-aware joins; the codebook has the canonical lists.
- **Strategic developments are not violence.** They include deals, defections, deployments. Filter by `event_type` if your question is about kinetic activity.

## Common Mistakes

| Mistake | Fix |
|---|---|
| Treating ACLED fatality totals as the casualty count | Cross-check with WHO, ICRC, Bellingcat, official MoH numbers. ACLED is conservative. |
| Counting all events as independent | Multi-day campaigns are coded as one event per day per location; the unit isn't "incident". |
| Using `country` filter for wars that cross borders | Combine countries; many conflicts span Sahel/Maghreb/Sudan-South Sudan boundaries. |
| Filtering only on `actor1` | An actor often appears as `actor2` or `assoc_actor_1`. Use union queries. |
| No User-Agent | ACLED logs and may rate-limit anonymous bulk callers. Identify the client. |
| Caching the live endpoint as if it were static | Recent rows can be edited as new sources surface. Re-pull the last 30 days; older history is stable. |

## Caching Pattern

ACLED is append-mostly for older periods, edit-prone for the recent month. Cache the historical bulk and refresh the recent window:

```python
import pathlib, time
CACHE = pathlib.Path("cache/acled"); CACHE.mkdir(parents=True, exist_ok=True)

def cached_acled(country: str, year: int, refresh_recent_days: int = 30) -> pd.DataFrame:
    path = CACHE / f"{country}-{year}.parquet"
    if path.exists():
        return pd.read_parquet(path)
    df = acled_events(country=country,
                      event_date_start=f"{year}-01-01",
                      event_date_end=f"{year}-12-31")
    df.to_parquet(path)
    return df
```

For the trailing 30 days, refresh on every run.

## Cross-References

- **REQUIRED: Apply `handling-credentials-safely`.** ACLED requires both `key` AND `email` as query string parameters — both are credential-shaped and must be redacted from any URL appearing in errors, summaries, or ledger notes.
- Output rows feed `building-evidence-ledger`. Each cited ACLED event becomes one row, with `source_grade` graded on the underlying `source` (often **B** for international wires, **C** for subnational reporting).
- Pair with `geolocating-imagery` when an ACLED event references images that need verification.
- For background on conflict patterns, see `analysing-military-lens`.
- For the methodology, ACLED's codebook is at `acleddata.com/resources` — read it before relying on a specific column.
