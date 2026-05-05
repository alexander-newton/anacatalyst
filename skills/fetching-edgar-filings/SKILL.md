---
name: fetching-edgar-filings
description: Use when the analyst needs the actual filings of a US-listed company — 10-K annual report, 10-Q quarterly, 8-K material event, 13F holdings, S-1 IPO, 6-K foreign-issuer report, proxy statements. Triggers include "what does the 10-K say", "look up filings for ticker X", "what did the company disclose", "13F holdings", "8-K material event", any case where corporate disclosures are the primary source.
---

# Fetching SEC Filings via EDGAR

## Overview

EDGAR (Electronic Data Gathering, Analysis, and Retrieval) is the public archive of every filing made with the US Securities and Exchange Commission since 1994. Public companies file with EDGAR; private companies don't. The analyst uses EDGAR for exact text of disclosures — risk factors, segment results, material events, insider holdings — that re-reports paraphrase or omit.

**Core principle:** *Cite the filing, not the article that cited the filing.* EDGAR is free, has no API key, and the original document is one URL away. There is no excuse for laundering corporate disclosures through journalism.

## When to Use

- Pulling the exact text of a risk-factor disclosure, MD&A discussion, segment breakdown, or contingent-liability note.
- Tracking insider ownership (Form 4) and institutional holdings (13F).
- Monitoring 8-K material-event filings as a real-time signal — material disclosures are often filed *before* press releases or wire reporting catches them.
- Building a complete filing history for a named company.

**Skip for:**
- Private companies (file with state regulators or, sometimes, internationally — not EDGAR).
- Real-time trades / order flow (consolidated tape, not EDGAR).
- Foreign issuers' home-market filings — EDGAR has 6-K and 20-F for foreign filers, but home-country regulators (Companies House, Handelsregister, INPI) hold more.

## Setup — No Key Required, But...

EDGAR has no API key. **But** the SEC's terms of use require a `User-Agent` header identifying the caller with a real contact email. Anonymous or generic User-Agents get rate-limited and eventually blocked.

```
EDGAR_USER_AGENT="strategic-analyst your-email@example.com"
```

All requests must use it. The SEC also rate-limits to ~10 requests/second; pace accordingly.

```python
import os, httpx
UA = os.environ["EDGAR_USER_AGENT"]
# Refuse to run with the placeholder email — SEC may permit it transiently but
# the rule is "real reachable contact". A request that gets rate-limited days
# later when this caller re-appears with @example.com is the worst-case outcome.
assert "@example.com" not in UA, (
    "EDGAR_USER_AGENT is the placeholder. Set it to a real reachable email per "
    "SEC's terms of use before making EDGAR requests."
)
HEADERS = {
    "User-Agent": UA,
    "Accept-Encoding": "gzip, deflate",
}
```

**Empirical confirmation (verified 2026-05):** a request to `https://www.sec.gov/Archives/...` with a plain `User-Agent: python-httpx` returns **HTTP 403** with body `"<title>SEC.gov | Your Request Originates from an Undeclared..."`. SEC's enforcement of the User-Agent rule is automatic and immediate — not a hypothetical risk. Any caller without a properly-formatted UA gets blocked at request time.

## The Three Endpoints

### A. Look up a CIK by ticker or name

EDGAR uses CIK (Central Index Key), not ticker, as the canonical company ID. Translate first:

```python
def edgar_cik_for_ticker(ticker: str) -> str | None:
    r = httpx.get("https://www.sec.gov/files/company_tickers.json",
                  headers=HEADERS, timeout=30)
    r.raise_for_status()
    for entry in r.json().values():
        if entry["ticker"].upper() == ticker.upper():
            return str(entry["cik_str"]).zfill(10)  # CIK is 10-digit, zero-padded
    return None
```

Cache `company_tickers.json`; it's ~1MB and changes rarely.

### B. Get the filing index for a CIK

```
GET https://data.sec.gov/submissions/CIK{cik}.json
```

Returns the company's most-recent ~1000 filings as parallel arrays (form, filingDate, accessionNumber, primaryDocument). Older filings are paginated; the response includes pointers.

```python
def edgar_filings(cik: str) -> "pd.DataFrame":
    import pandas as pd
    r = httpx.get(f"https://data.sec.gov/submissions/CIK{cik}.json",
                  headers=HEADERS, timeout=30)
    r.raise_for_status()
    recent = r.json().get("filings", {}).get("recent", {})
    return pd.DataFrame(recent)
```

Common forms worth filtering for:

| Form | What |
|---|---|
| `10-K` | Annual report (audited) |
| `10-Q` | Quarterly (unaudited) |
| `8-K` | Material event — typically within 4 business days |
| `S-1` | IPO registration |
| `S-3`, `S-4` | Shelf, M&A registrations |
| `DEF 14A` | Definitive proxy — exec comp, governance |
| `4` | Insider transactions |
| `13F-HR` | Institutional holdings (≥$100M AUM) |
| `13D` / `13G` | Beneficial ownership ≥5% |
| `6-K`, `20-F`, `40-F` | Foreign-issuer filings |
| `SC TO-T` / `SC TO-I` | Tender offers |

### C. Fetch a specific filing's documents

```
GET https://www.sec.gov/Archives/edgar/data/{cik_no_zeros}/{accession_no_no_dashes}/{primaryDocument}
```

`primaryDocument` is usually an `.htm` (the main filing); the same directory holds attachments and exhibits.

```python
def edgar_filing_url(cik: str, accession: str, primary: str) -> str:
    cik_int = int(cik)  # strip leading zeros
    accn_clean = accession.replace("-", "")
    return f"https://www.sec.gov/Archives/edgar/data/{cik_int}/{accn_clean}/{primary}"
```

To get the *content*, fetch the URL with the User-Agent and parse with `selectolax` or `BeautifulSoup`. Filings are HTML with predictable section headers; use anchor-based extraction rather than offset-based.

## Worked Example — last 8-Ks for AAPL, in time order

```python
cik = edgar_cik_for_ticker("AAPL")          # "0000320193"
filings = edgar_filings(cik)
eightk = filings[filings["form"] == "8-K"].sort_values("filingDate", ascending=False).head(10)
for _, row in eightk.iterrows():
    url = edgar_filing_url(cik, row["accessionNumber"], row["primaryDocument"])
    print(row["filingDate"], row["items"], url)
```

The `items` column lists the 8-K item codes filed (e.g., `2.02` = results of operations, `5.02` = officer changes). Filtering by item code is often more useful than by form alone.

## The XBRL Companion API

For *structured* financial data (reported numbers, not raw filings), EDGAR exposes XBRL via:

```
GET https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json
```

This returns every reported XBRL fact across all filings — revenue, net income, segment results, contingent liabilities — with dates and source-filing references. Useful for time series of reported numbers without re-parsing each filing.

```python
def edgar_company_facts(cik: str) -> dict:
    r = httpx.get(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json",
                  headers=HEADERS, timeout=60)
    r.raise_for_status()
    return r.json()  # {"facts": {"us-gaap": {...}, "dei": {...}}}
```

For a specific fact across companies, use the `frames` endpoint instead:

```
GET https://data.sec.gov/api/xbrl/frames/us-gaap/Revenues/USD/CY2023.json
```

## Common Mistakes

| Mistake | Fix |
|---|---|
| Quoting from a press release that summarised a 10-K | Pull the 10-K. Press releases routinely omit risk factors and contingent-liability notes that change the read. |
| Treating the *earliest* 8-K item as the most material | The latest 8-K usually supersedes earlier ones on the same topic; check item numbers and item-by-item amendments. |
| Relying on the press-release exhibit attached to an 8-K | The exhibit is often what the company *wanted* to disclose; the 8-K body and the *financial schedules* are what they *had* to disclose. The schedules are where the news is. |
| Missing 13F filings as a holdings signal | 13F is filed within 45 days of quarter-end. Useful for "did Big Holder X actually unwind their position", less useful for real-time positioning. |
| Failing to match XBRL fact concept names | `us-gaap:Revenues` vs `us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax` — different concepts, different periods of use. The XBRL US Approved Concept list is authoritative. |
| Single-segment view of a multi-segment business | The segment footnote often discloses the divisional breakdown the headline result hides. |
| Ignoring rate limits | Burst > 10 req/s gets throttled; sustained gets blocked. Respect the limit and use Accept-Encoding gzip. |
| Generic User-Agent | EDGAR explicitly requires a contact email in UA. Generic UAs are rate-limited. |

## Caching Pattern

Filings are immutable once published. Cache the document text by `accessionNumber`:

```python
import pathlib, hashlib
CACHE = pathlib.Path("cache/edgar"); CACHE.mkdir(parents=True, exist_ok=True)

def cached_filing(cik: str, accession: str, primary: str) -> str:
    key = hashlib.sha256(f"{cik}|{accession}|{primary}".encode()).hexdigest()[:16]
    path = CACHE / f"{key}.html"
    if path.exists():
        return path.read_text()
    url = edgar_filing_url(cik, accession, primary)
    r = httpx.get(url, headers=HEADERS, timeout=60)
    r.raise_for_status()
    path.write_text(r.text)
    return r.text
```

The filings index for a company changes whenever a new filing is made; refresh it on each session, but cache the document bodies indefinitely.

## Cross-References

- Output feeds `building-evidence-ledger` at A1 grade — these are primary documents.
- For the analytical use of corporate filings (e.g., risk-factor analysis, contingent-liability mapping), the relevant lens skills are `analysing-economic-lens` and `analysing-public-finance-lens`.
- For non-US companies, see (when written): Companies House (UK), Handelsregister (DE), INPI (FR), or aggregators like OpenCorporates.
- Archive filings via `archiving-with-wayback` when a specific 8-K is being cited — SEC retains everything but a snapshot is still useful for the audit trail.
