---
name: fetching-news-gdelt
description: Use when the analyst needs global news coverage of a topic at scale — across languages and source countries — beyond what RSS or generic web search returns. Triggers include "what's the global coverage of X", "how is X being reported in country Y", "tone of coverage", "narrative clustering", any volume-of-coverage question, and any case where a single Anglophone outlet would underrepresent the story.
---

# Fetching News via GDELT

## Overview

GDELT 2.0's Doc API is the strategic analyst's default tool for **global news at scale**. It indexes 100+ languages, surfaces source-country and tone metadata, and is free and key-less. It is **not** a clean dataset — quality varies wildly across sources, and naive use produces noisy results. The skill is in the query, the modes, and the post-processing.

**Core principle:** *GDELT is a wide net, not a curated list.* Every fetched article needs grading via `building-evidence-ledger`. The volume metric is for spotting; the article-level claim is for sourcing.

## When to Use

- Quantifying **how much** is being said about a topic, where, and in what tone.
- Finding stories surfacing in **non-English media** before the Anglophone wires pick them up.
- **Narrative clustering** across many outlets — what are the 3 main story-frames?
- Spotting **divergence** between domestic-media coverage in country X and external coverage of country X.
- Building a **time series of coverage volume** as an indicator (geopolitical attention, market-relevant attention, sentiment shifts).

**Skip for:**
- A single primary-source citation — go to the actual statement / dataset.
- Real-time breaking news (GDELT lags 15 minutes; wires are faster).
- High-credibility-only output — GDELT will ingest blogs, low-quality aggregators, and even some scraped sites.

## The API

**Endpoint:** `https://api.gdeltproject.org/api/v2/doc/doc`

No API key required. Polite usage: identify your client in the User-Agent.

**Key query parameters:**

| Param | Use |
|---|---|
| `query` | Boolean keyword query. Supports `AND`, `OR`, quoted phrases, `near` proximity, `sourcelang:`, `sourcecountry:`, `theme:`, `tone>N` |
| `mode` | Output type — see below |
| `format` | `json` (use this) or `html`/`csv` |
| `startdatetime` / `enddatetime` | YYYYMMDDHHMMSS (UTC). Window ≤ 72 hours for `artlist`; longer windows downsample |
| `maxrecords` | Up to 250 per request for `artlist` |
| `sort` | `datedesc`, `dateasc`, `tonedesc`, `toneasc`, `hybridrel` |

**The five modes worth knowing:**

| Mode | Returns |
|---|---|
| `artlist` | Article-level results (URL, title, source, date, language, tone, ngrams) — the workhorse |
| `timelinevol` | Hourly volume of coverage as a percentage of all news — for the "is attention rising" question |
| `timelinetone` | Hourly average tone (-10 to +10) — for sentiment shifts |
| `timelinesourcecountry` | Volume by source country over time — who is covering this |
| `tonechart` | Tone histogram bucketed — distribution of sentiment, useful for finding the negative tail |

## Worked Example — last 24h coverage of a CB rate decision

```python
import httpx, pandas as pd

GDELT = "https://api.gdeltproject.org/api/v2/doc/doc"
HEADERS = {"User-Agent": "strategic-analyst/0.1 (contact: you@example.com)"}

def gdelt_artlist(query: str, hours_back: int = 24, max_records: int = 250) -> pd.DataFrame:
    from datetime import datetime, timezone, timedelta
    end = datetime.now(timezone.utc)
    start = end - timedelta(hours=hours_back)
    fmt = "%Y%m%d%H%M%S"
    params = {
        "query": query,
        "mode": "artlist",
        "format": "json",
        "startdatetime": start.strftime(fmt),
        "enddatetime": end.strftime(fmt),
        "maxrecords": max_records,
        "sort": "datedesc",
    }
    r = httpx.get(GDELT, params=params, headers=HEADERS, timeout=30)
    r.raise_for_status()
    articles = r.json().get("articles", [])
    return pd.DataFrame(articles)

# Boolean query: include the entity, narrow to monetary-policy framing,
# exclude obvious noise. Quotes for exact phrases.
q = '("central bank" OR "policy rate" OR repo) AND (Turkey OR TCMB) AND ("rate cut" OR "rate decision" OR easing)'
df = gdelt_artlist(q, hours_back=24)
```

The returned DataFrame columns (current schema; verify against the live response):

| Column | Type | Notes |
|---|---|---|
| `url` | str | Article URL |
| `url_mobile` | str | Mobile variant if any |
| `title` | str | Article title |
| `seendate` | str (YYYYMMDDHHMMSS) | First-seen by GDELT |
| `socialimage` | str | OG image URL |
| `domain` | str | Root domain — **use this to deduplicate, not the URL** |
| `language` | str | ISO code or English name |
| `sourcecountry` | str | Country of source (best-effort) |

## Post-processing the Output

GDELT's `artlist` is noisy. Always:

1. **Deduplicate by domain** — many sites republish wires. Keep first-seen per domain per topic.
2. **Filter blocklist** — maintain a `domain_blocklist.txt` of known low-quality / SEO-spam / republisher domains.
3. **Cluster by title similarity or embedding** — TF-IDF cosine ≥ 0.6 or `sentence-transformers` for narrative clustering.
4. **Map to source hierarchy** — use the source-hierarchy table from `strategic-news-analysis` to grade by domain (Reuters/AP/AFP/Bloomberg = wire; FT/NYT/WSJ = quality national; etc.).
5. **Record in evidence ledger** — for any article that ends up cited, populate the row per `building-evidence-ledger`.

## Building Query Strings — Common Patterns

| Goal | Query pattern |
|---|---|
| Entity X + topic Y, English-language only | `(X OR alias) AND (Y OR synonym) sourcelang:eng` |
| Entity X in non-English coverage | `X sourcelang:tur OR sourcelang:rus ...` |
| Coverage from country C | `X sourcecountry:CN` |
| Negative-tone outliers | `X AND tone<-3` |
| Theme-coded events | `theme:GOV_REFORM`, `theme:ECON_INFLATION`, `theme:ARMEDCONFLICT` (full theme list at api.gdeltproject.org) |
| Proximity (X within 10 words of Y) | `X NEAR10 Y` |

## Caveats

- **Always pin `startdatetime` and `enddatetime`. Never use `timespan=Xh` for any output that will be cited.** A relative window is anchored on call time — two analysts running the same query five minutes apart get two different datasets, and reproducibility evaporates. The `timespan` parameter is for screen-poking only.
- **15-minute lag.** GDELT is not real-time. For breaking moves, supplement with RSS (`fetching-rss-watchlist`) and direct primary fetches.
- **`sourcecountry` is best-effort.** Inferred from domain TLD and content; can be wrong, especially for `.com` domains.
- **Tone scoring is shallow.** Built on a static lexicon; sarcasm, irony, and code-switched language confuse it. Useful for *aggregate* shifts, unreliable per-article.
- **No content text.** `artlist` returns metadata, not body text. Fetch and parse separately (`trafilatura` or `selectolax`) if you need text — and respect each site's robots.txt.
- **Republisher chains.** A wire from Reuters can appear on 200 domains; `sourcecountry` and `domain` reflect the *republisher*, not the originator. The evidence-ledger row should attribute to the wire, not the republisher.
- **Aggressive cap of 250 records per call.** For larger pulls, page by time window (e.g. 6-hour slices) and concatenate. Add a 1-second sleep between calls.

## Common Mistakes

| Mistake | Fix |
|---|---|
| Treating `artlist` results as "the news today" | They are an indexed sample with quality variance. Filter and grade. |
| Keyword query with no boolean structure | Use `AND`/`OR`/quoted phrases. A bare query produces too-broad results. |
| Counting domains as independent sources | Two domains running the same wire = one source. Deduplicate at the wire level. |
| Using `tone` per-article as evidence | Use it aggregated; per-article tone is noisy. |
| No User-Agent | GDELT will throttle anonymous high-volume callers. Identify yourself. |
| No caching | GDELT is fast but you'll burn time and risk throttling. Cache responses by query+window in `cache/gdelt/`. |
| Forgetting to log the query in the evidence ledger | The query *is* the methodology. Record it. |

## Caching Pattern

Cache responses by hash of `(query, startdatetime, enddatetime, mode)`:

```python
import hashlib, json, pathlib
def cache_key(query, start, end, mode):
    return hashlib.sha256(f"{query}|{start}|{end}|{mode}".encode()).hexdigest()[:16]
# Save df.to_parquet(cache_dir / f"{key}.parquet"); load on subsequent runs.
```

GDELT's window is fixed once specified, so cached responses are safe to reuse indefinitely *for that window*.

## Cross-References

- **REQUIRED: Apply `handling-credentials-safely` for any paired authenticated calls.** GDELT itself is keyless, but a typical workflow combines GDELT discovery with NewsAPI / OpenSanctions / OpenCorporates lookups that *do* take keys; the same redaction discipline applies wherever a key is touched in the same orchestration.
- Output rows feed `building-evidence-ledger`. Record the GDELT query string in the ledger's `notes` column for every cited article — the query is the reproducible bit.
- For named-outlet tracking (the same outlets every day), prefer `fetching-rss-watchlist` — cleaner and faster.
- For the post-fetch grading and clustering, use the source hierarchy in `strategic-news-analysis` and the synthesis triage in `synthesising-strategic-assessment`.
- The reference Python client `gdeltdoc` (`pip install gdeltdoc`) wraps the same endpoints — useful, but the raw httpx pattern above is more transparent and easier to debug.
