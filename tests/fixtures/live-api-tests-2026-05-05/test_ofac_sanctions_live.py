"""Live API test for fetching-ofac-sanctions skill."""
import os
import sys
import json
from pathlib import Path
from io import StringIO

# Load .env
env_path = Path(__file__).resolve().parents[1] / ".env"
if env_path.exists():
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

import httpx
import pandas as pd

KEY = os.environ.get("OPENSANCTIONS_KEY", "")
print("=" * 60)
print("STEP 2: env check")
print("=" * 60)
print(f"OPENSANCTIONS_KEY present: {bool(KEY)}; length={len(KEY)}")

SDN_HEADERS = ["ent_num", "name", "sdn_type", "program", "title", "call_sign",
               "vess_type", "tonnage", "grt", "vess_flag", "vess_owner", "remarks"]


def ofac_sdn() -> pd.DataFrame:
    r = httpx.get("https://www.treasury.gov/ofac/downloads/sdn.csv",
                  timeout=60, headers={"User-Agent": "strategic-analyst/0.1"})
    r.raise_for_status()
    return pd.read_csv(StringIO(r.text), header=None, names=SDN_HEADERS,
                       quotechar='"', encoding="latin-1")


def ofac_search(name: str) -> pd.DataFrame:
    df = ofac_sdn()
    return df[df["name"].str.contains(name, case=False, na=False)]


print()
print("=" * 60)
print("STEP 3: OFAC SDN direct CSV download")
print("=" * 60)
try:
    df = ofac_sdn()
    print(f"SDN row count: {len(df)}")
    print(f"Has >10,000 rows: {len(df) > 10000}")
    print(f"Columns: {list(df.columns)}")
    print(f"Sample row 0: name={df.iloc[0]['name']!r}, program={df.iloc[0]['program']!r}")
except Exception as e:
    print(f"FAILED: {type(e).__name__}: {e}")

print()
print("--- ofac_search('ROSNEFT') ---")
try:
    hits = ofac_search("ROSNEFT")
    print(f"Hit count: {len(hits)}")
    print("Top 3:")
    for i, row in hits.head(3).iterrows():
        print(f"  [{i}] name={row['name']!r}")
        print(f"       program={row['program']!r}")
        print(f"       sdn_type={row['sdn_type']!r}")
except Exception as e:
    print(f"FAILED: {type(e).__name__}: {e}")


# OpenSanctions
HEADERS = {"User-Agent": "strategic-analyst/0.1"}
if KEY:
    HEADERS["Authorization"] = f"ApiKey {KEY}"


def opensanctions_match(name: str, schema: str = "Person") -> dict:
    payload = {"queries": {"q1": {"schema": schema, "properties": {"name": [name]}}}}
    r = httpx.post("https://api.opensanctions.org/match/sanctions",
                   json=payload, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.json()


print()
print("=" * 60)
print("STEP 4: OpenSanctions match API — Yevgeny Prigozhin")
print("=" * 60)
try:
    result_en = opensanctions_match("Yevgeny Prigozhin", schema="Person")
    print(f"Call succeeded. Top-level keys: {list(result_en.keys())}")
    matches_en = result_en.get("responses", {}).get("q1", {}).get("results", [])
    print(f"Matches returned (English): {len(matches_en)}")
    print("Top 2:")
    for m in matches_en[:2]:
        name = m.get("caption") or (m.get("properties", {}).get("name") or [""])[0]
        score = m.get("score")
        match_flag = m.get("match")
        datasets = m.get("datasets", [])
        print(f"  - name={name!r} score={score} match={match_flag}")
        print(f"    datasets[{len(datasets)}]: {datasets[:8]}{'...' if len(datasets) > 8 else ''}")

    # Cross-list aggregation check on top hit
    if matches_en:
        top = matches_en[0]
        ds = top.get("datasets", [])
        suggestive = [d for d in ds if d in {"us_ofac_sdn", "eu_fsf", "gb_hmt_sanctions",
                                              "un_sc_sanctions", "ca_named_research_orgs"}]
        print(f"Top match cross-list datasets seen: {suggestive}")
        print(f"Total datasets on top match: {len(ds)}")
except httpx.HTTPStatusError as e:
    print(f"HTTP {e.response.status_code}: {e.response.text[:500]}")
except Exception as e:
    print(f"FAILED: {type(e).__name__}: {e}")


print()
print("=" * 60)
print("STEP 5: Cyrillic vs Latin transliteration")
print("=" * 60)
try:
    result_ru = opensanctions_match("Евгений Пригожин", schema="Person")
    matches_ru = result_ru.get("responses", {}).get("q1", {}).get("results", [])
    print(f"Cyrillic matches returned: {len(matches_ru)}")
    print("Top 2 Cyrillic:")
    for m in matches_ru[:2]:
        name = m.get("caption")
        print(f"  - {name!r} score={m.get('score')} match={m.get('match')}")

    # Compare entity IDs
    ids_en = {m.get("id") for m in matches_en}
    ids_ru = {m.get("id") for m in matches_ru}
    overlap = ids_en & ids_ru
    only_en = ids_en - ids_ru
    only_ru = ids_ru - ids_en
    print()
    print(f"Latin entity IDs:    {len(ids_en)}")
    print(f"Cyrillic entity IDs: {len(ids_ru)}")
    print(f"Overlap:             {len(overlap)}")
    print(f"Only-Latin:          {len(only_en)}")
    print(f"Only-Cyrillic:       {len(only_ru)}")
    print(f"Sets identical:      {ids_en == ids_ru}")
    if only_en:
        print(f"Only-Latin sample: {list(only_en)[:3]}")
    if only_ru:
        print(f"Only-Cyrillic sample: {list(only_ru)[:3]}")
except httpx.HTTPStatusError as e:
    print(f"HTTP {e.response.status_code}: {e.response.text[:500]}")
except Exception as e:
    print(f"FAILED: {type(e).__name__}: {e}")

print()
print("DONE")
