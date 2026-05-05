"""Live API smoke test for the fetching-edgar-filings skill.

Validates the documented edgar_cik_for_ticker, edgar_filings,
edgar_filing_url and XBRL companyfacts patterns against the real
SEC EDGAR endpoints, plus tests the User-Agent enforcement rule.
"""
from __future__ import annotations

import os
import pathlib
import re
import sys
import time
from collections import Counter

# 1. Load .env -------------------------------------------------------------
try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv(str(pathlib.Path(__file__).resolve().parents[3] / "/.env".lstrip("/")))
    print("[env] loaded via python-dotenv")
except Exception as exc:
    print(f"[env] python-dotenv unavailable ({exc!r}); falling back to manual parse")
    env_path = (pathlib.Path(__file__).resolve().parents[3] / ".env")
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

UA = os.environ.get("EDGAR_USER_AGENT", "")
print(f"[env] EDGAR_USER_AGENT non-empty: {bool(UA)} (len={len(UA)})  contains '@': {'@' in UA}")
assert UA, "EDGAR_USER_AGENT missing"
assert "@" in UA, "EDGAR_USER_AGENT must contain a contact email"

import httpx  # noqa: E402
import pandas as pd  # noqa: E402

HEADERS = {
    "User-Agent": UA,
    "Accept-Encoding": "gzip, deflate",
}

# 2. CIK lookup -----------------------------------------------------------
def edgar_cik_for_ticker(ticker: str) -> str | None:
    r = httpx.get("https://www.sec.gov/files/company_tickers.json",
                  headers=HEADERS, timeout=30)
    r.raise_for_status()
    for entry in r.json().values():
        if entry["ticker"].upper() == ticker.upper():
            return str(entry["cik_str"]).zfill(10)
    return None


print("\n[step 3] Looking up CIK for AAPL ...")
t0 = time.time()
cik = edgar_cik_for_ticker("AAPL")
print(f"  -> CIK={cik}  expected=0000320193  match={cik == '0000320193'}  ({time.time()-t0:.2f}s)")
assert cik == "0000320193"

time.sleep(0.2)  # rate-limit politeness

# 3. Filings index --------------------------------------------------------
def edgar_filings(cik: str) -> pd.DataFrame:
    r = httpx.get(f"https://data.sec.gov/submissions/CIK{cik}.json",
                  headers=HEADERS, timeout=30)
    r.raise_for_status()
    recent = r.json().get("filings", {}).get("recent", {})
    return pd.DataFrame(recent)


print("\n[step 4] Fetching filings index ...")
t0 = time.time()
filings = edgar_filings(cik)
print(f"  -> {len(filings)} filings, columns={list(filings.columns)[:8]}...  ({time.time()-t0:.2f}s)")
assert len(filings) > 0, "filings DataFrame empty"

eightk = filings[filings["form"] == "8-K"].sort_values("filingDate", ascending=False)
print(f"  -> 8-K count in recent index: {len(eightk)}")

time.sleep(0.2)

# 4. Most-recent 8-K body -------------------------------------------------
def edgar_filing_url(cik: str, accession: str, primary: str) -> str:
    cik_int = int(cik)
    accn_clean = accession.replace("-", "")
    return f"https://www.sec.gov/Archives/edgar/data/{cik_int}/{accn_clean}/{primary}"


print("\n[step 5] Fetching most-recent 8-K body ...")
top = eightk.iloc[0]
url = edgar_filing_url(cik, top["accessionNumber"], top["primaryDocument"])
print(f"  filingDate={top['filingDate']}  items={top.get('items', '')}")
print(f"  accession={top['accessionNumber']}  primary={top['primaryDocument']}")
print(f"  URL={url}")

t0 = time.time()
r = httpx.get(url, headers=HEADERS, timeout=60)
print(f"  HTTP={r.status_code}  body_bytes={len(r.content)}  ({time.time()-t0:.2f}s)")
assert r.status_code == 200
body = r.text
assert len(body) >= 1024, f"body smaller than 1KB ({len(body)} bytes)"
ct = r.headers.get("content-type", "")
print(f"  content-type={ct}  looks_html={'html' in ct.lower() or '<html' in body[:2000].lower()}")

# Extract item codes (8-K item references like 2.02, 5.02 etc.) ----------
# Look for "Item 5.02" / "Item  2.02" patterns in plaintext-extracted body.
text_only = re.sub(r"<[^>]+>", " ", body)
text_only = re.sub(r"\s+", " ", text_only)
item_refs = sorted(set(re.findall(r"Item\s+(\d{1,2}\.\d{2})", text_only)))
print(f"  item codes found in body: {item_refs}")
print(f"  filingDate (from index): {top['filingDate']}")
print(f"  body size: {len(body)} bytes")

time.sleep(0.5)

# 5. User-Agent enforcement test -----------------------------------------
print("\n[step 6] Testing request WITHOUT EDGAR_USER_AGENT (plain python-httpx UA) ...")
bad_headers = {"User-Agent": "python-httpx", "Accept-Encoding": "gzip, deflate"}
attempts = []
for i in range(3):
    t0 = time.time()
    try:
        rb = httpx.get(url, headers=bad_headers, timeout=30)
        attempts.append((rb.status_code, len(rb.content), rb.headers.get("content-type", ""),
                         rb.text[:200].replace("\n", " ")))
        print(f"  attempt {i+1}: HTTP={rb.status_code} bytes={len(rb.content)} ct={rb.headers.get('content-type','')[:60]}")
    except Exception as e:
        attempts.append(("EXC", str(e)[:200], "", ""))
        print(f"  attempt {i+1}: EXCEPTION {type(e).__name__}: {e}")
    time.sleep(0.3)

# Also try the submissions endpoint with bad UA (data.sec.gov is stricter)
print("\n  (also testing data.sec.gov submissions endpoint with bad UA)")
try:
    rb2 = httpx.get(f"https://data.sec.gov/submissions/CIK{cik}.json",
                    headers=bad_headers, timeout=30)
    print(f"  data.sec.gov bad-UA: HTTP={rb2.status_code} bytes={len(rb2.content)} ct={rb2.headers.get('content-type','')[:60]}")
    print(f"  body[:300]={rb2.text[:300]!r}")
except Exception as e:
    print(f"  data.sec.gov bad-UA: EXCEPTION {type(e).__name__}: {e}")

time.sleep(0.5)

# 6. XBRL companyfacts ----------------------------------------------------
print("\n[step 7] Fetching XBRL companyfacts ...")
t0 = time.time()
rf = httpx.get(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json",
               headers=HEADERS, timeout=60)
print(f"  HTTP={rf.status_code} bytes={len(rf.content)} ({time.time()-t0:.2f}s)")
assert rf.status_code == 200
facts = rf.json()
us_gaap = facts.get("facts", {}).get("us-gaap", {})
print(f"  total us-gaap concepts: {len(us_gaap)}")

# Count facts (sum of unit-array lengths) per concept
counts = []
for concept, payload in us_gaap.items():
    n = 0
    for unit, arr in payload.get("units", {}).items():
        n += len(arr)
    counts.append((concept, n))
counts.sort(key=lambda x: x[1], reverse=True)
print(f"  top 5 us-gaap concepts by fact count:")
for c, n in counts[:5]:
    print(f"    {c}: {n}")

print("\n[done] all checks passed.")
