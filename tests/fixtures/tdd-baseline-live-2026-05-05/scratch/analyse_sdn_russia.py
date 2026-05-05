"""Drill into the Russia-program vessels block — flag distribution, types, recent additions if datable."""
from __future__ import annotations
import sys, json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
df = pd.read_parquet(ROOT / "cache" / "ofac" / "sdn.parquet")
print(f"SDN total rows: {len(df)}")

programs = df["program"].fillna("").astype(str)
russia_mask = programs.str.contains("RUSSIA", case=False, na=False)
russia = df[russia_mask].copy()
print(f"Russia-program total: {len(russia)}")

# By sdn_type
print("\nRussia-program rows by sdn_type:")
print(russia["sdn_type"].fillna("(blank)").value_counts().head(15).to_string())

# Vessels — flag distribution
russia_vessels = russia[russia["sdn_type"].fillna("").str.upper().str.contains("VESSEL", na=False)].copy()
print(f"\nRussia-program vessels: {len(russia_vessels)}")
print("\nFlag-of-convenience analysis (vessel flag):")
print(russia_vessels["vess_flag"].fillna("(none)").value_counts().head(20).to_string())

# Vessel-type distribution
print("\nVessel-type distribution:")
print(russia_vessels["vess_type"].fillna("(none)").value_counts().head(15).to_string())

# Tonnage distribution (parse numerically where possible)
def parse_grt(x):
    try:
        return int(float(str(x).replace(",", "").replace("-", "0").strip())) if x and pd.notna(x) else 0
    except:
        return 0

russia_vessels["grt_int"] = russia_vessels["grt"].apply(parse_grt)
big = russia_vessels[russia_vessels["grt_int"] > 50000]  # large tankers
print(f"\nLarge (GRT > 50k) Russia-program vessels: {len(big)}")
print(big[["ent_num", "name", "vess_type", "vess_flag", "grt_int"]].head(20).to_string(index=False))

# Tanker-only filter
tanker_mask = russia_vessels["vess_type"].fillna("").str.contains("Tanker|tanker|Crude|crude|Oil|oil", regex=True, na=False)
tankers = russia_vessels[tanker_mask]
print(f"\nRussia-program TANKERS specifically: {len(tankers)}")
print("Top flag distribution among Russia-program tankers:")
print(tankers["vess_flag"].fillna("(none)").value_counts().head(15).to_string())

# Sample names
print("\nSample of 30 Russia-program tankers:")
print(tankers[["ent_num", "name", "vess_type", "vess_flag"]].head(30).to_string(index=False))

# Look for Sovcomflot-named vessels
sovcom = russia[russia["name"].fillna("").str.contains("SOVCOMFLOT|SCF", case=False, regex=True, na=False)]
print(f"\nSovcomflot-name matches in Russia-program SDN: {len(sovcom)}")
print(sovcom[["ent_num", "name", "sdn_type"]].head(10).to_string(index=False))

# Save filtered datasets
out = ROOT / "cache" / "ofac"
russia_vessels.to_csv(out / "russia_vessels_full.csv", index=False)
tankers.to_csv(out / "russia_tankers.csv", index=False)

summary = {
    "russia_total_entries": int(len(russia)),
    "russia_vessels_total": int(len(russia_vessels)),
    "russia_tankers_specifically": int(len(tankers)),
    "russia_vessels_grt_over_50k": int(len(big)),
    "top_flags_among_russia_vessels": russia_vessels["vess_flag"].fillna("(none)").value_counts().head(10).to_dict(),
    "top_vessel_types": russia_vessels["vess_type"].fillna("(none)").value_counts().head(10).to_dict(),
    "sovcomflot_matches": int(len(sovcom)),
}
(out / "russia_summary.json").write_text(json.dumps(summary, indent=2, default=str))
print(f"\nrussia_summary.json saved")
