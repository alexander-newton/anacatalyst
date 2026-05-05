"""Live API test for fetching-fred-macro skill (temporary, delete after run)."""
import os, time, traceback, json, pathlib, datetime as dt

# Load .env
env_path = (pathlib.Path(__file__).resolve().parents[3] / ".env")
for line in env_path.read_text().splitlines():
    line = line.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    k, v = line.split("=", 1)
    v = v.strip().strip('"').strip("'")
    os.environ.setdefault(k, v)

assert os.environ.get("FRED_API_KEY"), "FRED_API_KEY missing"
print(f"[OK] FRED_API_KEY loaded, length={len(os.environ['FRED_API_KEY'])}")

import pandas as pd
import httpx

results = {}

# --- Pattern A: pandas_datareader ---
print("\n=== Pattern A: pandas_datareader -> CPIAUCSL ===")
try:
    from pandas_datareader import data as pdr
    t0 = time.time()
    cpi_a = pdr.DataReader("CPIAUCSL", "fred", dt.date(2020, 1, 1))
    elapsed = time.time() - t0
    print(f"  shape={cpi_a.shape}, dtype={cpi_a.dtypes.to_dict()}, elapsed={elapsed:.2f}s")
    print(f"  index name={cpi_a.index.name}, columns={list(cpi_a.columns)}")
    print(f"  head:\n{cpi_a.head(2)}")
    print(f"  tail:\n{cpi_a.tail(3)}")
    results["pattern_a"] = {
        "ok": True,
        "rows": len(cpi_a),
        "columns": list(cpi_a.columns),
        "index_name": cpi_a.index.name,
        "last_date": str(cpi_a.index[-1].date()),
        "last_value": float(cpi_a.iloc[-1, 0]),
    }
except Exception as e:
    traceback.print_exc()
    results["pattern_a"] = {"ok": False, "error": repr(e)}

# --- Pattern B: direct httpx ---
print("\n=== Pattern B: direct httpx -> DFEDTARU ===")
FRED_KEY = os.environ["FRED_API_KEY"]
FRED = "https://api.stlouisfed.org/fred"

def fred_series(series_id: str, start: str = "2020-01-01") -> pd.DataFrame:
    r = httpx.get(
        f"{FRED}/series/observations",
        params={
            "series_id": series_id,
            "api_key": FRED_KEY,
            "file_type": "json",
            "observation_start": start,
        },
        timeout=30,
    )
    print(f"  HTTP status: {r.status_code}")
    r.raise_for_status()
    obs = r.json()["observations"]
    df = pd.DataFrame(obs)
    df["date"] = pd.to_datetime(df["date"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    return df.set_index("date")[["value"]].rename(columns={"value": series_id})

def fred_meta(series_id: str) -> dict:
    r = httpx.get(
        f"{FRED}/series",
        params={"series_id": series_id, "api_key": FRED_KEY, "file_type": "json"},
        timeout=30,
    )
    print(f"  meta HTTP status: {r.status_code}")
    r.raise_for_status()
    return r.json()["seriess"][0]

try:
    t0 = time.time()
    dfedtaru = fred_series("DFEDTARU", "2020-01-01")
    elapsed = time.time() - t0
    print(f"  shape={dfedtaru.shape}, dtypes={dfedtaru.dtypes.to_dict()}, elapsed={elapsed:.2f}s")
    print(f"  index name={dfedtaru.index.name}, columns={list(dfedtaru.columns)}")
    print(f"  head:\n{dfedtaru.head(2)}")
    print(f"  tail:\n{dfedtaru.tail(3)}")
    last_valid = dfedtaru.dropna()
    results["pattern_b"] = {
        "ok": True,
        "rows": len(dfedtaru),
        "columns": list(dfedtaru.columns),
        "index_name": dfedtaru.index.name,
        "last_date": str(last_valid.index[-1].date()),
        "last_value": float(last_valid.iloc[-1, 0]),
    }
except Exception as e:
    traceback.print_exc()
    results["pattern_b"] = {"ok": False, "error": repr(e)}

# --- fred_meta call ---
print("\n=== fred_meta(CPIAUCSL) ===")
try:
    meta = fred_meta("CPIAUCSL")
    keys_of_interest = ["units", "frequency", "seasonal_adjustment", "last_updated", "id", "title"]
    extracted = {k: meta.get(k) for k in keys_of_interest}
    print(json.dumps(extracted, indent=2))
    results["meta"] = {
        "ok": True,
        "has_units": "units" in meta,
        "has_frequency": "frequency" in meta,
        "has_seasonal_adjustment": "seasonal_adjustment" in meta,
        "has_last_updated": "last_updated" in meta,
        "values": extracted,
    }
except Exception as e:
    traceback.print_exc()
    results["meta"] = {"ok": False, "error": repr(e)}

# --- Caching pattern ---
print("\n=== Caching pattern: cached_series ===")
CACHE = (pathlib.Path(__file__).resolve().parents[3] / "cache/fred")
CACHE.mkdir(parents=True, exist_ok=True)

def cached_series(series_id: str, max_age_hours: int = 6) -> pd.DataFrame:
    path = CACHE / f"{series_id}.parquet"
    if path.exists() and (time.time() - path.stat().st_mtime) / 3600 < max_age_hours:
        print(f"  [CACHE HIT] reading {path}")
        return pd.read_parquet(path)
    print(f"  [CACHE MISS] fetching {series_id} from FRED")
    df = fred_series(series_id)
    df.to_parquet(path)
    return df

try:
    cache_path = CACHE / "CPIAUCSL.parquet"
    if cache_path.exists():
        cache_path.unlink()

    print("First call (expect MISS):")
    t0 = time.time()
    df1 = cached_series("CPIAUCSL")
    miss_time = time.time() - t0
    assert cache_path.exists(), "Cache file not written"
    print(f"  miss took {miss_time:.3f}s, file size = {cache_path.stat().st_size} bytes")

    print("Second call (expect HIT):")
    t0 = time.time()
    df2 = cached_series("CPIAUCSL")
    hit_time = time.time() - t0
    print(f"  hit took {hit_time:.3f}s")

    same = df1.equals(df2)
    print(f"  DataFrames equal: {same}")
    print(f"  Speed-up: {miss_time / max(hit_time, 1e-6):.1f}x")
    results["cache"] = {
        "ok": True,
        "miss_time_s": miss_time,
        "hit_time_s": hit_time,
        "speedup": miss_time / max(hit_time, 1e-6),
        "frames_equal": same,
        "short_circuited": hit_time < miss_time / 2,
    }
except Exception as e:
    traceback.print_exc()
    results["cache"] = {"ok": False, "error": repr(e)}

print("\n\n=== SUMMARY ===")
print(json.dumps(results, indent=2, default=str))
