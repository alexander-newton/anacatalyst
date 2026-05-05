"""Try alternate URLs for the OFAC recent-actions feed (the documented one 404'd)."""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from _safe import safe_get  # noqa: E402

UA = {"User-Agent": "strategic-analyst/0.1"}

candidates = [
    "https://ofac.treasury.gov/recent-actions/feed",
    "https://ofac.treasury.gov/recent-actions/recent-actions.xml",
    "https://ofac.treasury.gov/recent-actions",
    "https://ofac.treasury.gov/feeds/recent-actions",
    "https://home.treasury.gov/feeds/press-releases-rss-feed/all",
    "https://ofac.treasury.gov/news",
    "https://home.treasury.gov/system/files/126/recent-actions.xml",
    "https://ofac.treasury.gov/sanctions-list-service",
]

for u in candidates:
    try:
        r = safe_get(u, timeout=20, follow_redirects=True, headers=UA)
        print(f"OK {r.status_code} len={len(r.text)} url={u} ctype={r.headers.get('content-type','?')[:40]}")
    except Exception as e:
        print(f"-- {type(e).__name__}: {str(e)[:160]} :: {u}")
