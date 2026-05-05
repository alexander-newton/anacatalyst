"""Live API smoke test for the fetching-eia-energy skill.

Validates the documented eia_series + caching + browse patterns
against the real EIA Open Data API.
"""
from __future__ import annotations

import os
import pathlib
import sys
import time

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

KEY = os.environ.get("EIA_API_KEY", "")
print(f"[env] EIA_API_KEY non-empty: {bool(KEY)} (len={len(KEY)})")
assert KEY, "EIA_API_KEY missing"

# 2. Imports ---------------------------------------------------------------
import httpx  # noqa: E402
import pandas as pd  # noqa: E402

print(f"[deps] httpx={httpx.__version__} pandas={pd.__version__}")

# 3. Series API pattern (verbatim from SKILL.md) ---------------------------
def eia_series(series_id: str) -> pd.DataFrame:
    r = httpx.get(
        f"https://api.eia.gov/v2/seriesid/{series_id}",
        params={"api_key": KEY},
        timeout=30,
        headers={"User-Agent": "strategic-analyst/0.1"},
    )
    print(f"[http] GET /seriesid/{series_id} -> {r.status_code}")
    r.raise_for_status()
    payload = r.json()
    data = payload.get("response", {}).get("data", [])
    df = pd.DataFrame(data)
    if not df.empty:
        df["period"] = pd.to_datetime(df["period"])
        df = df.set_index("period").sort_index()
    return df, payload


def eia_browse(route: str, **facets) -> dict:
    params = {"api_key": KEY}
    for k, vs in facets.items():
        for v in vs:
            params.setdefault(f"facets[{k}][]", []).append(v)
    r = httpx.get(
        f"https://api.eia.gov/v2/{route}/data/",
        params=params,
        timeout=30,
        headers={"User-Agent": "strategic-analyst/0.1"},
    )
    print(f"[http] GET /{route}/data/ -> {r.status_code}")
    r.raise_for_status()
    return r.json()


# 4. Fetch the two series --------------------------------------------------
print("\n--- WTI Cushing daily (PET.RWTC.D) ---")
wti, wti_payload = eia_series("PET.RWTC.D")
print(f"[wti] rows={len(wti)} columns={list(wti.columns)}")
print(f"[wti] dtypes:\n{wti.dtypes}")
print(f"[wti] head:\n{wti.head(2)}")
print(f"[wti] tail:\n{wti.tail(3)}")

print("\n--- Cushing crude inventory weekly (PET.W_EPC0_SAX_YCUOK_MBBL.W) ---")
cushing, cushing_payload = eia_series("PET.W_EPC0_SAX_YCUOK_MBBL.W")
print(f"[cushing] rows={len(cushing)} columns={list(cushing.columns)}")
print(f"[cushing] tail:\n{cushing.tail(3)}")

# 5. Validate plausibility -------------------------------------------------
def numeric_value(df: pd.DataFrame) -> pd.Series:
    # value column may be string -> coerce
    return pd.to_numeric(df["value"], errors="coerce")

wti_val = numeric_value(wti).dropna()
cush_val = numeric_value(cushing).dropna()

last_wti_date = wti_val.index[-1]
last_wti = float(wti_val.iloc[-1])
last_cush_date = cush_val.index[-1]
last_cush = float(cush_val.iloc[-1])

print(f"\n[plausibility] last WTI: {last_wti} on {last_wti_date.date()} (range 40-120: {40<=last_wti<=120})")
print(f"[plausibility] last Cushing inv: {last_cush} on {last_cush_date.date()} (range 15-50: {15<=last_cush<=50})")

# 6. Caching pattern -------------------------------------------------------
CACHE = (pathlib.Path(__file__).resolve().parents[3] / "cache/eia")
CACHE.mkdir(parents=True, exist_ok=True)

CACHE_HIT_FLAG = {"hit": False}

def cached_eia(series_id: str, max_age_hours: float = 6) -> pd.DataFrame:
    path = CACHE / f"{series_id}.parquet"
    if path.exists() and (time.time() - path.stat().st_mtime) / 3600 < max_age_hours:
        CACHE_HIT_FLAG["hit"] = True
        print(f"[cache] HIT  {path}")
        return pd.read_parquet(path)
    print(f"[cache] MISS {path} (fetching)")
    df, _ = eia_series(series_id)
    df.to_parquet(path)
    return df

# Force a fresh write
target = CACHE / "PET.RWTC.D.parquet"
if target.exists():
    target.unlink()

print("\n--- Caching: first call (should MISS, fetch, write) ---")
CACHE_HIT_FLAG["hit"] = False
df1 = cached_eia("PET.RWTC.D")
assert not CACHE_HIT_FLAG["hit"], "first call must be a miss"
assert target.exists(), "parquet not written"
print(f"[cache] file size = {target.stat().st_size} bytes, rows={len(df1)}")

print("\n--- Caching: second call (should HIT, no HTTP) ---")
CACHE_HIT_FLAG["hit"] = False
df2 = cached_eia("PET.RWTC.D")
assert CACHE_HIT_FLAG["hit"], "second call must be a hit"
print(f"[cache] hit returned rows={len(df2)} cols={list(df2.columns)}")

# 7. Metadata via browse pattern ------------------------------------------
print("\n--- Metadata via /seriesid/ (top-level metadata fields) ---")
# Inspect what metadata the seriesid endpoint already exposes
top = wti_payload.get("response", {})
meta_keys = [k for k in top.keys() if k != "data"]
print(f"[meta] response top-level keys: {list(top.keys())}")
for k in meta_keys:
    val = top[k]
    if isinstance(val, (list, dict)) and len(str(val)) > 200:
        print(f"[meta] {k}: <len={len(val)}>")
    else:
        print(f"[meta] {k}: {val}")

# Try /v2/seriesid/PET.RWTC.D (no /data/) — already what we called.
# The skill's "fred_meta-equivalent" hint -> use eia_browse on the petroleum/pri/spt route
# to pull facet metadata.
print("\n--- Browse petroleum/pri/spt route (eia_browse) ---")
try:
    browse = eia_browse("petroleum/pri/spt", series=["RWTC"])
    resp = browse.get("response", {})
    print(f"[browse] keys: {list(resp.keys())}")
    print(f"[browse] frequency: {resp.get('frequency')}")
    print(f"[browse] description: {resp.get('description')}")
    if "data" in resp and resp["data"]:
        sample = resp["data"][-1]
        print(f"[browse] last data row: {sample}")
except Exception as exc:
    print(f"[browse] FAILED: {exc!r}")

# Also try the explicit metadata endpoint
print("\n--- Probe /v2/petroleum/pri/spt (no /data/) for catalogue metadata ---")
try:
    r = httpx.get(
        "https://api.eia.gov/v2/petroleum/pri/spt",
        params={"api_key": KEY},
        timeout=30,
        headers={"User-Agent": "strategic-analyst/0.1"},
    )
    print(f"[meta-route] status={r.status_code}")
    r.raise_for_status()
    md = r.json().get("response", {})
    print(f"[meta-route] keys: {list(md.keys())}")
    print(f"[meta-route] frequency: {md.get('frequency')}")
    print(f"[meta-route] startPeriod={md.get('startPeriod')} endPeriod={md.get('endPeriod')}")
    if "facets" in md:
        print(f"[meta-route] facets: {[f.get('id') for f in md['facets']]}")
except Exception as exc:
    print(f"[meta-route] FAILED: {exc!r}")

print("\n=== ALL DONE ===")
print(f"WTI:      {last_wti} on {last_wti_date.date()}")
print(f"Cushing:  {last_cush} on {last_cush_date.date()}")
