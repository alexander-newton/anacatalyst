"""Scrape the OFAC recent-actions HTML page (the RSS URL has 404'd)."""
from __future__ import annotations
import re, sys, json, datetime as dt
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from _safe import safe_get  # noqa: E402

OUT = Path(__file__).resolve().parents[2] / "cache" / "ofac"
OUT.mkdir(parents=True, exist_ok=True)
UA = {"User-Agent": "strategic-analyst/0.1"}

URL = "https://ofac.treasury.gov/recent-actions"

r = safe_get(URL, timeout=30, follow_redirects=True, headers=UA)
html = r.text
(OUT / "recent_actions.html").write_text(html, encoding="utf-8")
print(f"recent-actions HTML: {len(html)} bytes")

# The page lists recent OFAC actions in a table. Extract item titles + dates by structural pattern.
# Drupal-style markup: each action has a date and a title link.
# Heuristic regex: find <a href="/recent-actions/<num>" ...>...</a> with adjacent date.
# Strip tags, keep dates + headlines.

# Try generic pattern: <h3> ... <a href=...> with action-date class
items = re.findall(
    r'<a[^>]+href="(/recent-actions/\d+)"[^>]*>(.*?)</a>',
    html, flags=re.DOTALL,
)
unique = []
seen = set()
for href, text in items:
    text_clean = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", text)).strip()
    if href in seen or not text_clean:
        continue
    seen.add(href)
    unique.append((href, text_clean))

print(f"\nFound {len(unique)} unique action links. First 25:")
for h, t in unique[:25]:
    print(f"  {h} :: {t[:140]}")

# Also extract date strings near them — Drupal pages typically tag date elements
date_matches = re.findall(r'<time[^>]*datetime="([^"]+)"', html)
print(f"\n<time datetime> tags found: {len(date_matches)}")
for d in date_matches[:25]:
    print(f"  {d}")

# Filter for Russia / shadow / vessel keywords
kw = re.compile(r'\b(Russia|Russian|shadow|vessel|tanker|Sovcomflot|maritime|crude)\b', re.IGNORECASE)
relevant = [(h, t) for h, t in unique if kw.search(t)]
print(f"\nRussia/shadow/vessel/tanker filter: {len(relevant)} matches in headlines")
for h, t in relevant[:15]:
    print(f"  {h} :: {t[:160]}")

summary = {
    "accessed_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    "url": URL,
    "total_links": len(unique),
    "russia_related": [{"href": h, "text": t} for h, t in relevant[:30]],
    "recent_dates_found": date_matches[:25],
}
(OUT / "recent_actions_summary.json").write_text(json.dumps(summary, indent=2))
