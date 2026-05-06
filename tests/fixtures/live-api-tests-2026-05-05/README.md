# Live API tests — 2026-05-05

Four end-to-end live-API tests against the user's real keys, run via `uv run` from the project venv. First time the fetcher skills have been exercised against real endpoints rather than reasoned about from documentation.

## Per-test outcomes

### `test_fred_live.py` (FRED — `fetching-fred-macro`)

| Pattern | Result |
|---|---|
| A — `pandas_datareader` for `CPIAUCSL` | ✅ 75 monthly rows, last value **330.293** on 2026-03-01 |
| B — direct httpx for `DFEDTARU` | ⚠️ One run returned 200 OK (Fed funds upper bound = **3.75%** on 2026-05-05); a follow-up returned **502 Bad Gateway** transiently |
| `fred_meta(CPIAUCSL)` | ✅ Returned units (`Index 1982-1984=100`), frequency (`Monthly`), seasonal_adjustment, last_updated, id, title — exactly the metadata the skill documents |
| Caching (parquet round-trip) | ✅ Miss = 463ms, Hit = 15ms, **31× speed-up**, frames equal |

**Findings applied to the skill:**
- pyarrow is **required** for the caching pattern (without it `df.to_parquet()` raises `ImportError`). Skill now lists it as a uv dep.
- pandas-datareader is **optional** — only needed for Pattern A. Skill now flags this.
- FRED returns transient 5xx errors. Skill now recommends 3-attempt retry with exponential backoff.

### `test_edgar_live.py` (SEC EDGAR — `fetching-edgar-filings`)

| Step | Result |
|---|---|
| AAPL CIK lookup | ✅ Returned `0000320193`, matches documented value |
| Filings index | ✅ 1000 filings, **105 are 8-K** in the recent index |
| Most recent 8-K body fetch | ✅ Filed 2026-04-30, items `2.02,9.01`, body 37,639 bytes |
| **No-User-Agent control test** | ✅ **HTTP 403** with body `"Your Request Originates from an Undeclared..."` — three attempts, all blocked at request time |
| XBRL companyfacts | ✅ 200 OK, 3.7MB, 503 us-gaap concepts. Top 5 by fact count: EarningsPerShareBasic, EarningsPerShareDiluted, GrossProfit, NetIncomeLoss, CommonStockDividendsPerShareDeclared |

**Findings applied to the skill:**
- The "User-Agent required" rule is **empirically validated** — SEC's enforcement is automatic and immediate. The skill now records this verbatim.
- `EDGAR_USER_AGENT` in `.env.example` is the placeholder `your-email@example.com`. Skill now contains a startup `assert "@example.com" not in UA` and the README flags this in its Configuration section.

### `test_eia_live.py` (EIA — `fetching-eia-energy`)

| Step | Result |
|---|---|
| WTI Cushing daily (`PET.RWTC.D`) | ✅ 5,000 rows, last value **$99.89/BBL** on 2026-04-27 |
| Cushing inventory weekly (`PET.W_EPC0_SAX_YCUOK_MBBL.W`) | ✅ 1,151 rows, last value **29,772 MBBL (= 29.8 million barrels)** on 2026-04-24 |
| Caching | ❌ Failed — pyarrow not installed (same root cause as FRED; fixed via uv) |

**Schema drift discovered:** the response has **10 columns** (`duoarea`, `area-name`, `product`, `product-name`, `process`, `process-name`, `series`, `series-description`, `value`, `units`), not the 2 (`period`, `value`) the skill originally documented. Skill now contains the full schema table.

**Units convention:** `MBBL` = thousand barrels. A "29772" inventory value means **29.8 million barrels**, not 29 thousand. Always read the `units` column. Skill now warns explicitly.

**Bug found in `eia_browse`:** `params.setdefault(...).append(...)` doesn't serialise correctly for repeated query keys in httpx. Fixed in the skill — use list-of-tuples form.

### `test_acled_live.py` (ACLED — `fetching-acled-events`)

Three-step test exercising the OAuth 2.0 migration the API underwent in 2024-2025:

| Step | Result |
|---|---|
| Password grant against `acleddata.com/oauth/token` | ✅ HTTP 200, RFC-6749 response shape (`access_token`, `expires_in=86400s`, `refresh_token`, `token_type=Bearer`) |
| Authenticated read of Sudan events, 14–13 months ago (inside the 12-month publication-lag restriction) | ✅ HTTP 200, **100 rows**, all 31 documented columns present (`event_id_cnty`, `event_date`, `event_type`, `actor1`, `actor2`, `country`, `fatalities`, `location`, `latitude`, `longitude`, `notes`, etc.); sample 2025-02-09 Explosions/Remote violence by "Military Forces of Sudan (2019-)" |
| Refresh-token round-trip | ✅ HTTP 200, new access token returned, distinct from previous |

**Bugs surfaced and applied to the skill:**

1. **Auth contract correction.** The plan originally inferred RFC-6749 password-grant fields (`grant_type`, `username`, `password`). The live probe returned HTTP 400 `invalid_request` with hint `"Check the client_id parameter"`. ACLED's docs (https://acleddata.com/api-documentation/getting-started) require **two extra fields** the plan didn't have: `client_id="acled"` (a hardcoded public client identifier — no client_secret) and `scope="authenticated"` for the password grant. The refresh grant also needs `client_id="acled"`. Skill helper updated to include both.

2. **Account-level restrictions documented.** Free-tier ACLED accounts have a **12-month publication-lag** — events are not exposed to the API until they are at least 12 months old. The original test window (last 7 days) returned 0 rows even though Sudan has active daily events. Every ACLED response includes a `data_query_restrictions` block describing the active limits — skill now has a dedicated section explaining this and showing how to inspect it programmatically. Test window is now 14–13 months ago to respect the restriction.

3. **Worked example date moved** from 2026-03 (inside the restricted window — would return 0 rows for free-tier users) to 2024-04 (live-verified to return events with the documented schema).

The skill is now correct for the 2026 ACLED API; tested end-to-end against live data.

### `test_telegram_live.py` (Telegram — `fetching-telegram-channels`)

Two-part test exercising both access paths the skill documents:

| Part | Result |
|---|---|
| Unauthenticated `t.me/s/<channel>` HTML mirror (no credentials) | ✅ HTTP 200, 138KB body in 0.9s, 10 posts parsed from `@telegram` with the documented schema (`msg_id`, `url`, `datetime`, `views`, text preview) |
| Authenticated MTProto handshake (`TELEGRAM_API_ID` + `TELEGRAM_API_HASH`) | ✅ API_ID numeric 8-digit, API_HASH 32-hex-char, **handshake to DC 2 succeeded**, `is_user_authorised=False` (expected — no `.session` yet) |

**Discipline notes (the special bits for Telegram):**
- The probe uses `MemorySession()` so no `.session` file is written and no phone number gets bound to the test.
- No interactive auth was attempted (no SMS would have been sent). The first real authenticated run will trigger the phone-number prompt; that's a one-off on the user's terminal.
- `_safe.py`-equivalent `redact()` helper applied to any error path; credential values never printed (only lengths and shape characteristics).
- `*.session` and `*.session-journal` are gitignored as credentials.

The skill correctly documents both paths — unauthenticated for read-only browsing, authenticated for history/search/media. No skill corrections needed from this run.

### `test_sentinel_live.py` (Copernicus Data Space Ecosystem — `fetching-sentinel-imagery`)

| Step | Result |
|---|---|
| OAuth2 token (CDSE) | ✅ HTTP 200, 1,593-char Bearer token, 30-min expiry |
| STAC catalogue search (Sentinel-2 L2A, Strait of Hormuz, April 2026) | ⚠️ → ✅ — first attempt against `catalogue.dataspace.copernicus.eu/stac/` returned 0 features; switched to the SH-compatible endpoint at `sh.dataspace.copernicus.eu/api/v1/catalog/1.0.0/search`, returned **7 tiles**, best is S2C from 2026-04-07 with **1.54% cloud cover** |
| Process API (RGB render at 256×256) | ✅ HTTP 200 in 1.33s, **89,679-byte PNG** saved to `cache/sentinel/rgb-test.png` |

**Findings applied to the skill:**
- **CDSE has two catalogue surfaces.** `catalogue.dataspace.copernicus.eu/stac/` only exposes Copernicus Contributing Missions and CLMS burnt-area products — **not Sentinel-1/2 directly.** The correct catalogue for Sentinel-1/2 is the Sentinel Hub-compatible endpoint at `sh.dataspace.copernicus.eu/api/v1/catalog/1.0.0/`. Skill now documents both surfaces explicitly.
- Collection IDs are lowercase (`sentinel-2-l2a`, `sentinel-1-grd`) and match the Process API's `type` field exactly.
- Cloud-cover filtering should be done client-side after the search; the `eo:cloud_cover` query in the request body is ignored by the SH-compatible variant.

### `test_ofac_sanctions_live.py` (OFAC SDN + OpenSanctions — `fetching-ofac-sanctions`)

| Step | Result |
|---|---|
| OFAC SDN direct CSV download | ❌ **302 redirect to a new URL**: `https://sanctionslistservice.ofac.treas.gov/api/publicationpreview/exports/sdn.csv`. Default httpx doesn't follow redirects. |
| OpenSanctions match for "Yevgeny Prigozhin" | ✅ Top match score 1.0, cross-referenced against **28 datasets** including `us_ofac_sdn`, `eu_fsf` |
| Cyrillic vs Latin (`"Евгений Пригожин"` vs `"Yevgeny Prigozhin"`) | ✅ **Identical entity returned** — OpenSanctions does transliteration automatically |

**Findings applied to the skill:**
- Updated SDN URL to the new sanctionslistservice endpoint, with `follow_redirects=True` on the httpx call. The old `treasury.gov/ofac/downloads/` URLs still work via redirect but the call must follow them.
- Updated transliteration warning: OpenSanctions handles it automatically; cross-form queries are only needed when querying the raw OFAC/EU/OFSI lists directly.

## Security findings — keys exposed in agent output

Two keys appeared verbatim in subagent output during these runs:

- **`FRED_API_KEY`** — leaked in an httpx error traceback (the URL with `api_key=...` query string).
- **`EIA_API_KEY`** — printed verbatim by the EIA subagent in its summary.

Both are free, instantly-regenerable. Recommend rotating both in their respective portals and updating `.env`. The other live keys (ACLED, Comtrade, NewsAPI, AlphaVantage, OpenSanctions, EDGAR_USER_AGENT) were not exposed in agent output.

## Re-running

```bash
uv run python tests/fixtures/live-api-tests-2026-05-05/test_fred_live.py
uv run python tests/fixtures/live-api-tests-2026-05-05/test_eia_live.py
uv run python tests/fixtures/live-api-tests-2026-05-05/test_edgar_live.py
uv run python tests/fixtures/live-api-tests-2026-05-05/test_ofac_sanctions_live.py
```

Each runs end-to-end in under a minute against live APIs. Useful as a regression suite when SKILL.md schema or auth assumptions change.
