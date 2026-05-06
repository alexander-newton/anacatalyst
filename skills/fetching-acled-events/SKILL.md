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

Register a myACLED account at [acleddata.com/register](https://acleddata.com/register). Approval is automatic on email confirmation. **ACLED moved to OAuth 2.0 Bearer-token auth in 2026** — the legacy `key`+`email` query-string scheme is no longer accepted, and the `api.acleddata.com` subdomain is dead.

Set in `.env`:

```
ACLED_EMAIL=you@example.com
ACLED_PASSWORD=your-myacled-password
```

The skill exchanges these for a 24-hour access token at the token endpoint and caches it under `cache/acled/token.json`. Refresh tokens (14-day) are used for renewal so the password doesn't have to be re-sent on every cycle. The password sits in memory only; it is never put in a URL or printed.

**Endpoints:**
- Token: `https://acleddata.com/oauth/token`
- Read: `https://acleddata.com/api/acled/read`

**Authoritative documentation:**
- https://acleddata.com/acled-api-documentation
- https://acleddata.com/api-documentation/getting-started
- https://acleddata.com/api-documentation/acled-endpoint
- https://acleddata.com/api-documentation/elements-acleds-api

## The Workhorse Call

Two helpers: `_acled_token()` manages the OAuth dance with token caching; `acled_events()` is the analyst-facing fetcher. Apply `handling-credentials-safely` throughout — the password and tokens never appear in URLs, error messages, summaries, or cache filenames.

```python
import os, json, time, pathlib, httpx, pandas as pd
from typing import Optional

ACLED_EMAIL    = os.environ["ACLED_EMAIL"]
ACLED_PASSWORD = os.environ["ACLED_PASSWORD"]

TOKEN_URL = "https://acleddata.com/oauth/token"
READ_URL  = "https://acleddata.com/api/acled/read"
TOKEN_CACHE = pathlib.Path("cache/acled/token.json")
TOKEN_CACHE.parent.mkdir(parents=True, exist_ok=True)
SAFETY_MARGIN_S = 300  # refresh 5 min before nominal expiry


def _save_token(payload: dict) -> dict:
    """Persist token + computed expiry timestamp; chmod 600."""
    record = {
        "access_token":  payload["access_token"],
        "refresh_token": payload.get("refresh_token"),
        "expires_at":    int(time.time()) + int(payload.get("expires_in", 86400)),
        "token_type":    payload.get("token_type", "Bearer"),
    }
    TOKEN_CACHE.write_text(json.dumps(record))
    try:
        TOKEN_CACHE.chmod(0o600)
    except OSError:
        pass  # non-POSIX filesystem
    return record


def _post_token(data: dict) -> dict:
    """Token endpoint with credential-safe error handling.

    A 4xx from the token endpoint can echo the submitted password in the
    response body — never include `e.response.text` in the re-raised error.
    """
    try:
        r = httpx.post(TOKEN_URL, data=data, timeout=30,
                       headers={"User-Agent": "strategic-analyst/0.1"})
        r.raise_for_status()
        return r.json()
    except httpx.HTTPStatusError as e:
        raise RuntimeError(
            f"ACLED token endpoint returned {e.response.status_code}; "
            f"check ACLED_EMAIL / ACLED_PASSWORD in .env"
        ) from None


def _acled_token() -> str:
    """Return a valid access token; refresh-first fallback to password grant.

    ACLED's OAuth server requires `client_id="acled"` (a hardcoded public
    client identifier; no client_secret) on every grant request. The
    password grant additionally requires `scope="authenticated"`.
    Verified against the live API on 2026-05-05.
    """
    now = int(time.time())
    if TOKEN_CACHE.exists():
        rec = json.loads(TOKEN_CACHE.read_text())
        if rec.get("expires_at", 0) - SAFETY_MARGIN_S > now:
            return rec["access_token"]
        # Try refresh first — avoids re-sending the password.
        if rec.get("refresh_token"):
            try:
                payload = _post_token({
                    "grant_type":    "refresh_token",
                    "refresh_token": rec["refresh_token"],
                    "client_id":     "acled",
                })
                return _save_token(payload)["access_token"]
            except RuntimeError:
                pass  # fall through to password grant
    # Password grant — first use, or after a refresh-token failure.
    payload = _post_token({
        "grant_type": "password",
        "client_id":  "acled",
        "scope":      "authenticated",
        "username":   ACLED_EMAIL,
        "password":   ACLED_PASSWORD,
    })
    return _save_token(payload)["access_token"]


def acled_events(country: Optional[str] = None,
                 region: Optional[str] = None,
                 event_type: Optional[str] = None,
                 actor1: Optional[str] = None,
                 event_date_start: Optional[str] = None,
                 event_date_end: Optional[str] = None,
                 limit: int = 5000) -> pd.DataFrame:
    """Fetch ACLED events with the most useful filters.

    Dates: YYYY-MM-DD. Use event_date_start..event_date_end (BETWEEN logic).
    Country: full English name (e.g., 'Sudan'). Pipe-separated for multiple.
    Region: 1=Western Africa, 2=Middle Africa, ... see ACLED docs.
    Event type: 'Battles' | 'Explosions/Remote violence' | 'Violence against civilians'
                | 'Protests' | 'Riots' | 'Strategic developments'.
    """
    params = {"limit": limit}
    if country:    params["country"] = country
    if region:     params["region"] = region
    if event_type: params["event_type"] = event_type
    if actor1:
        params["actor1"] = actor1
        params["actor1_where"] = "LIKE"  # substring match
    if event_date_start and event_date_end:
        params["event_date"] = f"{event_date_start}|{event_date_end}"
        params["event_date_where"] = "BETWEEN"

    headers = {
        "Authorization": f"Bearer {_acled_token()}",
        "User-Agent": "strategic-analyst/0.1",
    }
    r = httpx.get(READ_URL, params=params, headers=headers, timeout=30)
    if r.status_code == 401:
        # Token may have been revoked early (admin action, password change).
        # Single retry: drop the cache, re-grant, retry once.
        TOKEN_CACHE.unlink(missing_ok=True)
        headers["Authorization"] = f"Bearer {_acled_token()}"
        r = httpx.get(READ_URL, params=params, headers=headers, timeout=30)
    r.raise_for_status()
    return pd.DataFrame(r.json().get("data", []))
```

Worked example — battles in Sudan, April 2024:

```python
df = acled_events(country="Sudan",
                  event_type="Battles",
                  event_date_start="2024-04-01",
                  event_date_end="2024-04-30")
# Live verification 2026-05-05: returns events with all 31 documented fields,
# sample row date=2024-04-03 type=Battles location=Nyala fatalities=3.
```

The first call triggers a password grant and writes `cache/acled/token.json`; subsequent calls (within 24 hours) reuse the cached access token; calls after expiry use the refresh token; the password is re-sent only when the refresh token has itself expired (~14 days) or has been revoked.

## Account-Level Query Restrictions (read this before debugging "no rows")

ACLED's free / standard accounts apply a **publication-lag restriction**: events are not exposed to the API until they are at least **12 months old**. A query for "Sudan, last 30 days" will return zero rows on a free-tier account — not because the data doesn't exist, but because the account isn't authorised to see it yet.

Every `acled_events()` response includes a `data_query_restrictions` block describing the active limits:

```json
{
  "data_query_restrictions": {
    "countries": [],
    "event_types": [],
    "regions": [],
    "history": [],
    "recency": [],
    "date_recency": {
      "quantity": 12,
      "unit": "Months",
      "description": "12 Months old",
      "timestamp": 1746493801,
      "date": "2025-05-06"
    }
  }
}
```

The `date_recency.date` field is the cutoff: queries must be entirely *before* this date. Other restriction fields (`countries`, `event_types`, `regions`, `history`, `recency`) describe other quota dimensions that empty arrays mean "no restriction" and populated arrays describe the allowed set.

**Operational consequence for the analyst:** ACLED is not a real-time wire. For analysis of events less than 12 months old you need either an enterprise-tier account (`describe.recency` lifted on registration) or a different data source — GDELT for tempo and narrative coverage, Bellingcat / ISW for verified-OSINT live tracking. The skill documents this at the design level rather than papering over it with a "live" claim that is structurally false.

Inspect restrictions programmatically when an empty result is suspicious:

```python
import httpx
r = httpx.get("https://acleddata.com/api/acled/read",
              params={"limit": 1},
              headers={"Authorization": f"Bearer {_acled_token()}"})
print(r.json()["data_query_restrictions"]["date_recency"])
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
| Committing `cache/acled/token.json` | It's a 24-hour bearer credential. `cache/` is gitignored — keep it that way. |
| Pasting `ACLED_PASSWORD` into a subagent prompt | Reference the env var by name; the subagent loads it via `os.environ` from `.env`. |
| Using a stale `ACLED_KEY` from before the OAuth migration | The legacy static key is no longer accepted. Replace with `ACLED_PASSWORD` — see API Setup. |

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

- **REQUIRED: Apply `handling-credentials-safely`.** ACLED's 2026 OAuth model is *safer* than the legacy query-string scheme — bearer tokens in headers don't leak in error tracebacks the way `key=...&email=...` URLs did. Remaining discipline:
  - The myACLED *password* in `ACLED_PASSWORD` is a higher-stakes credential than the old static key (it also opens the web account). Confirm presence by length only; never echo.
  - The cached `cache/acled/token.json` is a 24-hour bearer credential. `cache/` is gitignored; do not commit; do not paste the file path into screenshots or summaries.
  - On a 4xx from the token endpoint, do **not** include the response body in any error message — it can echo the submitted password.
- Output rows feed `building-evidence-ledger`. Each cited ACLED event becomes one row, with `source_grade` graded on the underlying `source` (often **B** for international wires, **C** for subnational reporting).
- Pair with `geolocating-imagery` when an ACLED event references images that need verification.
- For background on conflict patterns, see `analysing-military-lens`.
- For the methodology, ACLED's codebook is at `acleddata.com/resources` — read it before relying on a specific column.
