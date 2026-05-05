---
name: fetching-rss-watchlist
description: Use when the analyst needs daily or hourly tracking of a fixed list of named outlets — the analyst's "morning read" of FT World, Bloomberg Markets, Reuters Top, BBC, plus topical feeds and named experts. Triggers include "daily sweep", "watchlist", "what did [outlet] publish today", "morning brief", recurring monitoring of a named publication, and any case where deduplication across runs matters more than search recall.
---

# Fetching an RSS Watchlist

## Overview

RSS is the cheapest, most reliable way to track **named outlets** over time. Where GDELT casts a wide net, the watchlist is a curated whitelist — outlets the analyst already trusts at known reliability grades. Combined with a YAML config and a deduplication store, it produces the morning sweep without any per-day work.

**Core principle:** *The watchlist encodes the analyst's source hierarchy as code.* The grades from `building-evidence-ledger` come along for the ride — every fetched item already has an Admiralty source-grade attached because the watchlist itself does.

## When to Use

- Daily / hourly sweeps of a fixed set of outlets.
- Tracking a known story across the same outlets every day for change detection.
- Cheap, durable monitoring with **no API key** and **no rate-limit anxiety**.
- Keeping the analyst's source-quality discipline visible — the YAML config is auditable.

**Skip for:**
- Discovery (finding outlets you don't already follow). Use `fetching-news-gdelt`.
- Outlets that don't publish RSS or that ratelimit aggressively. Some major outlets have crippled their feeds — fall back to home-page scraping with `trafilatura`, but log it.
- Real-time wire feeds. Wires lag in RSS; pay for the wire if you need the speed.

## The Watchlist Config

Stored at the plugin/project level, e.g. `config/watchlist.yaml`:

```yaml
outlets:
  - name: Reuters Top News
    feed: https://www.reutersagency.com/feed/?best-topics=top-news&post_type=best
    source_grade: B           # wire service
    default_info_grade: 2
    region: global
  - name: FT World
    feed: https://www.ft.com/world?format=rss
    source_grade: B
    default_info_grade: 2
    region: global
  - name: Bloomberg Markets
    feed: https://feeds.bloomberg.com/markets/news.rss
    source_grade: B
    default_info_grade: 2
    region: global
  - name: TCMB Press Releases (EN)
    feed: https://www.tcmb.gov.tr/wps/wcm/connect/EN/TCMB+EN/Main+Menu/Announcements/Press+Releases?type=rss
    source_grade: A           # primary document
    default_info_grade: 1
    region: TR
  - name: ECB Press Releases
    feed: https://www.ecb.europa.eu/rss/press.html
    source_grade: A
    default_info_grade: 1
    region: EU

topics:
  - name: turkey-monetary-policy
    keywords: ["TCMB", "Turkey central bank", "lira", "policy rate"]
    outlets: ["Reuters Top News", "FT World", "Bloomberg Markets", "TCMB Press Releases (EN)"]
```

**Why YAML?** It's diffable in git, reviewable in PRs, and the analyst can see the source hierarchy at a glance. Don't push this into a database.

## The Fetcher

Minimal pattern using `feedparser`:

```python
import feedparser, yaml, hashlib, json, pathlib, datetime as dt

UA = "strategic-analyst/0.1 (contact: you@example.com)"
SEEN_DB = pathlib.Path("cache/rss_seen.json")

def load_watchlist(path: str) -> dict:
    return yaml.safe_load(open(path))

def fetch_outlet(outlet: dict) -> list[dict]:
    feed = feedparser.parse(outlet["feed"], agent=UA)
    items = []
    for entry in feed.entries:
        guid = entry.get("id") or entry.get("link")
        item_hash = hashlib.sha256(guid.encode()).hexdigest()[:16]
        items.append({
            "outlet": outlet["name"],
            "source_grade": outlet["source_grade"],
            "default_info_grade": outlet["default_info_grade"],
            "title": entry.get("title", ""),
            "link": entry.get("link", ""),
            "published": entry.get("published", ""),
            "summary": entry.get("summary", ""),
            "guid": guid,
            "item_hash": item_hash,
            "fetched_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        })
    return items

def filter_by_keywords(items: list[dict], keywords: list[str]) -> list[dict]:
    needles = [k.lower() for k in keywords]
    return [
        it for it in items
        if any(n in (it["title"] + " " + it["summary"]).lower() for n in needles)
    ]

def dedupe_against_seen(items: list[dict]) -> list[dict]:
    SEEN_DB.parent.mkdir(parents=True, exist_ok=True)
    seen = set(json.loads(SEEN_DB.read_text())) if SEEN_DB.exists() else set()
    new = [it for it in items if it["item_hash"] not in seen]
    seen.update(it["item_hash"] for it in items)
    SEEN_DB.write_text(json.dumps(sorted(seen)))
    return new

def sweep(watchlist_path: str, topic_name: str | None = None) -> list[dict]:
    wl = load_watchlist(watchlist_path)
    if topic_name:
        topic = next(t for t in wl["topics"] if t["name"] == topic_name)
        outlets = [o for o in wl["outlets"] if o["name"] in topic["outlets"]]
        keywords = topic["keywords"]
    else:
        outlets, keywords = wl["outlets"], None
    all_items = []
    for o in outlets:
        all_items.extend(fetch_outlet(o))
    if keywords:
        all_items = filter_by_keywords(all_items, keywords)
    return dedupe_against_seen(all_items)
```

Output is a list of dicts ready to feed into `building-evidence-ledger` — every row arrives with `source_grade` and `default_info_grade` already populated from the watchlist.

## Polite Fetching

- **User-Agent.** Identify the client. Anonymous bulk RSS hits get throttled or blocked by some publishers.
- **Cache-Control.** `feedparser` honours `etag` and `modified` if you pass them — store and reuse to avoid re-pulling unchanged feeds.
- **Rate.** Don't hit one outlet more than once a minute. If you need faster, you've outgrown RSS.
- **robots.txt.** Most RSS feeds are explicitly opt-in to bots, but if you're pairing this with HTML scraping, check.

```python
# Conditional GET on subsequent runs
feed = feedparser.parse(url, agent=UA, etag=last_etag, modified=last_modified)
if feed.status == 304:
    return []  # nothing new
```

## Common Mistakes

| Mistake | Fix |
|---|---|
| Single-string `keywords` instead of a list | Always a list — keeps OR semantics explicit. |
| No deduplication store | You'll see the same item every run. Persist `seen` hashes. |
| Trusting `entry.published` to be timezone-aware | Many feeds emit naive dates. Parse with `dateutil` and force UTC. |
| Fetching all outlets sequentially under a deadline | Use `asyncio` + `aiohttp` for parallel fetches when the watchlist grows beyond ~10 outlets. |
| Source grade hard-coded in the fetch loop | Put grades in the YAML, not in code. The whole point is auditability. |
| Discarding the GUID | Without it, deduplication is unreliable. Always carry the feed's GUID through. |
| Ignoring `summary` truncation | RSS summaries are often clipped. Don't quote from them as if they're the article — fetch the article body if a quote matters. |

## Watchlist Hygiene

- **Check feed health weekly.** Outlets break their RSS without warning. A `make check-feeds` rule that pings each feed and reports `200 / 304 / 404 / parse-error` is worth ten minutes a week.
- **Review grades quarterly.** An outlet's source-grade is not eternal. If their reporting deteriorates (new owner, new editorial line, repeated single-source scoops that don't hold up), downgrade.
- **Version the watchlist.** Commit changes; the diff *is* the audit trail of who-trusted-what-when.

## Cross-References

- Output items feed `building-evidence-ledger` directly. Each row already carries `source_grade` from the YAML; the analyst still has to set per-claim `info_grade` and add `primary_url` (the RSS item's link) and `archive_url`.
- For wider discovery beyond the watchlist, run `fetching-news-gdelt` in parallel.
- The watchlist's grade column is the operational manifestation of the source hierarchy from `strategic-news-analysis`.
- A morning sweep typically pairs this skill with `producing-daily-sitrep` (when written) — RSS in, sitrep out.
