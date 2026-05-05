---
name: fetching-ofac-sanctions
description: Use when the analyst needs to check whether a person, entity, vessel, or aircraft is subject to US, EU, UK, UN, or other sanctions — or to monitor sanctions designations / removals. Triggers include "is X sanctioned", "OFAC SDN check", "entity list", "is this designated", "who's been sanctioned today", any case where a sanctions hit-check is part of the analysis.
---

# Fetching Sanctions Data — OFAC, EU, UK, UN, and OpenSanctions

## Overview

Sanctions lookups are deceptively easy to get wrong. The same person may appear on three lists with three different name spellings; vessels are renamed and reflagged constantly; the SDN list alone has multiple programs with different prohibitions; and "designated by" is not the same as "subject to secondary sanctions". The skill is to query the right list correctly and to use entity-resolution where multiple lists converge.

**Core principle:** *Designation is binary; consequences are not.* Whether a name is "on the list" is one question; what flows from that (asset freeze, travel ban, secondary-sanctions exposure, sectoral prohibitions) requires reading the program's actual text, not the list entry.

## When to Use

- Hit-checking a named individual, entity, vessel, or aircraft against active sanctions lists.
- Monitoring new designations and removals (e.g., daily OFAC actions feed).
- Building a sanctions-exposure map for a counterparty or supply chain.
- Verifying a media claim about who has been sanctioned.

**Skip for:**
- Legal advice on the *consequences* of a designation — that's a compliance/legal question, not a research one.
- Export-controls (EAR / ITAR / Wassenaar) — those are BIS / State Department, not OFAC. Different lists.
- Internal company watchlists — these are not public.

## The Five Sources

### 1. OFAC SDN list (US Treasury) — the workhorse

The Specially Designated Nationals list. Free, no key.

**URL note (verified 2026-05):** the old `treasury.gov/ofac/downloads/` URLs now 302-redirect to a new sanctions-list service. Always pass `follow_redirects=True`, or use the new URL directly:

- **Current canonical CSV:** `https://sanctionslistservice.ofac.treas.gov/api/publicationpreview/exports/sdn.csv`
- **Older-style URLs (still work via redirect):** `https://www.treasury.gov/ofac/downloads/sdn.csv`, `sdn.xml`, `sdn_advanced.xml`, `add.csv`, `alt.csv`
- **Recent actions HTML page:** `https://ofac.treasury.gov/recent-actions` (verified 2026-05-05). The skill previously documented an RSS feed at `recent-actions/recent-actions-rss-feed` — that endpoint **404s** as of 2026-05. The HTML page is the working surface; scrape it for the action list. If a future RSS endpoint is restored, prefer it; until then, parse `<a>` tags under the actions table.
- **Sanctions Programs:** the SDN row tells you *which program* (e.g., `RUSSIA-EO14024`, `CYBER2`, `IRAN`); the program defines what's prohibited.

```python
import httpx, pandas as pd
SDN_HEADERS = ["ent_num","name","sdn_type","program","title","call_sign",
               "vess_type","tonnage","grt","vess_flag","vess_owner","remarks"]

def ofac_sdn() -> pd.DataFrame:
    # follow_redirects=True is non-optional — old treasury.gov URLs redirect to the
    # sanctionslistservice.ofac.treas.gov endpoint and httpx does not follow by default.
    r = httpx.get("https://sanctionslistservice.ofac.treas.gov/api/publicationpreview/exports/sdn.csv",
                  timeout=60, follow_redirects=True,
                  headers={"User-Agent": "strategic-analyst/0.1"})
    r.raise_for_status()
    from io import StringIO
    return pd.read_csv(StringIO(r.text), header=None, names=SDN_HEADERS,
                       quotechar='"', encoding="latin-1")

def ofac_search(name: str) -> pd.DataFrame:
    df = ofac_sdn()
    return df[df["name"].str.contains(name, case=False, na=False)]
```

For richer data — aliases, ID numbers, addresses — use `sdn_advanced.xml` or the per-program JSON files.

**Adjacent OFAC lists:**
- **SSI** — Sectoral Sanctions Identifications (Russia / Venezuela). Different prohibitions from SDN.
- **Non-SDN lists** — Foreign Sanctions Evaders, Palestinian Legislative Council, ad-hoc programs.

### 2. EU Consolidated Financial Sanctions list

Updated as published. XML feed:

```
https://webgate.ec.europa.eu/fsd/fsf/public/files/xmlFullSanctionsList_1_1/content
```

The EU list is structurally similar to OFAC but separately maintained — same person may appear on both with different transliterations. Always cross-check.

### 3. UK OFSI Consolidated List

```
https://ofsistorage.blob.core.windows.net/publishlive/ConList.csv
```

Post-Brexit, UK sanctions are separately administered. Many overlap with EU/UN, but the UK has its own designations (notably for some Russia-Ukraine and Belarus actors).

### 4. UN Security Council Consolidated List

```
https://scsanctions.un.org/resources/xml/en/consolidated.xml
```

Multilateral; binds all UN member states. Coverage is narrower than OFAC/EU but a UN designation is the strongest legal basis.

### 5. OpenSanctions — the aggregator with entity resolution

```
https://api.opensanctions.org
```

OpenSanctions (Friedrich Lindenberg's project) **aggregates 150+ sanctions, PEP, and watchlists**, deduplicates them, and provides entity-resolution. For a hit-check across all lists at once, this is the default.

```python
import os, httpx
KEY = os.environ.get("OPENSANCTIONS_KEY")
HEADERS = {"User-Agent": "strategic-analyst/0.1"}
if KEY:
    HEADERS["Authorization"] = f"ApiKey {KEY}"

def opensanctions_match(name: str, schema: str = "Person") -> dict:
    """schema: 'Person', 'Company', 'Organization', 'LegalEntity', 'Vessel'."""
    payload = {"queries": {"q1": {"schema": schema, "properties": {"name": [name]}}}}
    r = httpx.post("https://api.opensanctions.org/match/sanctions",
                   json=payload, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.json()
```

Returns scored matches with provenance — the underlying OFAC/EU/UN/UK list entry is included. For Pro-tier features (bulk download, deeper PEP coverage), the paid tier is ~£400/year.

## The Hit-Check Workflow

For an unfamiliar name, run all four canonical lists plus OpenSanctions:

```python
def hit_check(name: str) -> dict:
    return {
        "ofac_sdn": ofac_search(name).to_dict("records"),
        "opensanctions": opensanctions_match(name),
        # eu, ofsi, un — implement similarly
    }
```

Then for each hit:
1. Read the **program** the entry is under, not just the name match.
2. Note the **date of designation** — older entries may have been delisted.
3. Cross-check the **identifying data** — DOB, place of birth, ID numbers, addresses. Name-only matches have high false-positive rates (common names, transliteration variants).
4. **Transliteration on Cyrillic / Arabic / Chinese names.** OpenSanctions handles transliteration automatically — querying `"Yevgeny Prigozhin"` and `"Евгений Пригожин"` against `/match/sanctions` returns the same entity (verified 2026-05). For OpenSanctions-mediated lookups, one query is sufficient. **However, if querying raw OFAC SDN, EU FSF, or OFSI lists directly**, transliteration is *not* applied — query both forms there. The skill's value-add over OpenSanctions is that it normalises the cross-list aggregation; rely on it where possible.

## Common Mistakes

| Mistake | Fix |
|---|---|
| Citing "OFAC sanctioned X" without naming the program | OFAC has 50+ programs. The program is the prohibition; the name is the index. Always cite both. |
| Single-list check | Same actor often appears on multiple lists; missing one is missing the other regimes' prohibitions. Always check OFAC + EU + UK + UN + OpenSanctions. |
| Name-only match | High false-positive on common names. Cross-check DOB / POB / ID number / address. |
| Trusting Latin spelling for non-Latin names against raw OFAC/EU/OFSI lists | Query both forms (`"Yevgeniy Prigozhin"` AND `"Евгений Пригожин"`). OpenSanctions handles this for you; direct list queries do not. |
| Treating SSI like SDN | SSI prohibits *sectoral* activity (e.g., new debt over X days for designated Russian banks). It is not an asset freeze. Read the program. |
| Caching as if static | OFAC publishes daily updates. Caches must refresh at least daily; for live monitoring, hourly. |
| Confusing "designated entity" with "majority-owned by designated entity" | OFAC's 50% Rule: if a designated person owns ≥50% of an entity, that entity is *also* blocked, even if not on the list. The only way to detect this is corporate-structure data — OpenSanctions partially handles it via "ownership" relationships. |

## Caching Pattern

```python
import pathlib, time
CACHE = pathlib.Path("cache/ofac"); CACHE.mkdir(parents=True, exist_ok=True)

def cached_sdn(max_age_hours: int = 6) -> pd.DataFrame:
    path = CACHE / "sdn.parquet"
    if path.exists() and (time.time() - path.stat().st_mtime) / 3600 < max_age_hours:
        return pd.read_parquet(path)
    df = ofac_sdn()
    df.to_parquet(path)
    return df
```

Refresh OFAC at least daily for active investigations; the lists are updated in business hours US Eastern.

## Cross-References

- Output rows feed `building-evidence-ledger` at **A1 grade** — these are primary regulatory documents.
- The SDN row's `program` field links to the actual OFAC program description; cite both.
- For corporate-structure data (the 50% Rule), pair with `fetching-edgar-filings` for US-listed counterparties or OpenCorporates for global entity resolution.
- `analysing-political-lens` and `analysing-public-finance-lens` reach for sanctions data when the question turns on coercion or financial-sector exposure.
