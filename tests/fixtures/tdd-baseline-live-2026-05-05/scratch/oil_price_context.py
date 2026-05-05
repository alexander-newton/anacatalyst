"""Look at Brent + WTI trajectory through 2025-2026 to characterise the current spike."""
from __future__ import annotations
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
brent = pd.read_parquet(ROOT / "cache" / "eia" / "PET.RBRTE.D.parquet")
wti = pd.read_parquet(ROOT / "cache" / "eia" / "PET.RWTC.D.parquet")

for label, df in [("Brent", brent), ("WTI", wti)]:
    df = df.sort_index()
    df = df[df.index >= "2024-01-01"]
    print(f"\n=== {label} (PET.RBRTE.D / PET.RWTC.D) since 2024-01-01 ===")
    monthly_avg = df["value"].resample("MS").mean().round(2)
    print(monthly_avg.tail(18).to_string())
    # Identify YTD-2026 trajectory
    df_2026 = df[df.index >= "2026-01-01"]
    print(f"  2026 YTD: min={df_2026['value'].min():.2f} max={df_2026['value'].max():.2f} latest={df_2026['value'].iloc[-1]:.2f} on {df_2026.index[-1].date()}")
    # 30-day move
    if len(df) >= 30:
        last = df["value"].iloc[-1]
        m30 = df["value"].iloc[-30]
        print(f"  30-day chg: {m30:.2f} -> {last:.2f} ({(last/m30-1)*100:+.1f}%)")
