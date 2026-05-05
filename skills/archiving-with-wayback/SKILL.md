---
name: archiving-with-wayback
description: Use when a URL is being cited in an evidence ledger or assessment and a stable snapshot is needed because pages can disappear, change, or be paywalled later. Triggers include "archive this", "save a snapshot", "what did this page say last week", "Wayback", populating the archive_url column of an evidence ledger, and any case where the cited URL is not under the analyst's control.
---

# Archiving with Wayback Machine

## Overview

Pages disappear, get edited, or move behind paywalls. A citation without an archive snapshot ages into a broken link. The Wayback Machine (Internet Archive) is the analyst's default snapshot tool: free, unauthenticated, instant, and authoritative for chain-of-custody.

**Core principle:** *Archive at the moment of citation, not later.* By the time you need the snapshot — when a reviewer asks how the page read on the day you cited it — the live page may already have changed.

## When to Use

- Populating the `archive_url` column of any evidence-ledger row.
- Verifying *when* a page first appeared, *whether* it has changed, or *what* a removed page used to say.
- Capturing social-media posts before deletion (Twitter/X, Facebook, Telegram).
- Citing official statements that may be edited or retracted (central-bank releases, government press, corporate disclosures).

**Skip for:**
- Internal documents you control (your team's wiki, your own files).
- Subscription-only paywalled content that Wayback cannot crawl — note the paywall and rely on the original timestamp instead.
- Sites that explicitly block Wayback via robots.txt — note the block; consider archive.today as a fallback (see below).

## The Two Endpoints

The Wayback Machine has two operations the analyst needs:

### A. Save a snapshot (capture now)

```
POST https://web.archive.org/save/<full-url>
```

Returns the snapshot URL in the `Content-Location` header (or a 302 redirect) once capture completes.

```python
import httpx
def save_to_wayback(url: str, timeout: int = 30) -> str | None:
    r = httpx.get(f"https://web.archive.org/save/{url}",
                  follow_redirects=True, timeout=timeout,
                  headers={"User-Agent": "strategic-analyst/0.1"})
    if r.status_code == 200 and "/web/" in str(r.url):
        return str(r.url)
    return None
```

Or via curl:

```bash
curl -sL -A "strategic-analyst/0.1" \
  "https://web.archive.org/save/https://example.gov/announcement" \
  -o /dev/null -w "%{url_effective}\n"
```

The `waybackpy` library (`pip install waybackpy`) wraps both operations in a tidier API; useful if you're archiving in volume.

### B. Look up an existing snapshot (provenance / change history)

```
GET https://archive.org/wayback/available?url=<url>&timestamp=<YYYYMMDD>
```

Returns nearest snapshot URL and timestamp.

```python
def find_nearest_snapshot(url: str, when: str = "20260101") -> dict | None:
    r = httpx.get("https://archive.org/wayback/available",
                  params={"url": url, "timestamp": when},
                  timeout=20)
    return r.json().get("archived_snapshots", {}).get("closest")
```

Use this to answer:
- *When did this page first appear?* (look up timestamp `19960101`, take the earliest snapshot).
- *What did this page say last week?* (look up timestamp from a week ago).
- *Did this page change?* (compare snapshot text across two timestamps).

## Worked Example — populating an evidence-ledger row

```python
url = "https://www.tcmb.gov.tr/wps/wcm/.../press-release-2026-05-05"
snapshot = save_to_wayback(url)
# returns e.g. "https://web.archive.org/web/20260505123412/https://www.tcmb.gov.tr/.../press-release-2026-05-05"
ledger_row["archive_url"] = snapshot or "not located"
ledger_row["accessed_at"] = "2026-05-05T12:34:12Z"
```

If `save_to_wayback` returns `None` (rate-limited, robots.txt block, server error), the analyst:

1. Records `archive_url: not located` honestly.
2. Notes the reason in the row's `notes` column ("Wayback save returned 429" / "robots.txt block").
3. Falls back to `archive.today` (see below).
4. Captures a screenshot as last resort, with the timestamp embedded.

## Fallback: archive.today

For pages Wayback cannot capture (paywall, robots.txt, JavaScript-heavy SPAs that Wayback fails to render), `archive.today` (also `archive.ph` / `archive.is`) often works.

```bash
# Submit
curl -sL -A "strategic-analyst/0.1" \
  -d "url=https://example.com/page" \
  https://archive.ph/submit/
# Look up an existing capture: https://archive.ph/<full-url>
```

archive.today has no public API, so submission is HTML-form-based. Less elegant but it captures things Wayback can't.

## Common Mistakes

| Mistake | Fix |
|---|---|
| Archiving "later" | Capture *at the moment of citation*. The live page has already begun drifting. |
| Citing only `archive_url`, dropping the original `primary_url` | Both belong in the ledger. The original is the citation; the snapshot is the proof. |
| Trusting the snapshot timestamp blindly | The timestamp is *when Wayback first crawled*, not necessarily when the page was first published. Cross-check with the page's own date header. |
| Treating "no Wayback hit" as "page never existed" | Wayback's coverage is broad but not universal. Try archive.today, then a Google cache search, then a screenshot. |
| Archiving social media via the URL only | X/Twitter pages render JS-late; Wayback often captures the loading shell. Use the [tweet's-permalink](https://web.archive.org/web/<url>) form, or use a tool like `nitter.net` mirror first then archive that. |
| Forgetting to record the snapshot timestamp | Both columns are needed: `archive_url` *and* `accessed_at` (your local fetch time). The mismatch between them is itself a finding. |
| Submitting volume bursts | Wayback rate-limits aggressive callers. Pace at ≤ 1 request per 4–5 seconds for sustained bulk archiving. |

## Caveats

- **Wayback honours robots.txt, retroactively.** If a site adds an aggressive `Disallow: /` to their robots.txt, Wayback hides their *historical* snapshots too. Old archives can disappear.
- **Capture may be partial.** Embedded images, fonts, and JS often fail to capture. The text is usually preserved; layout sometimes isn't.
- **The submission may be queued.** Some sites with heavy infrastructure are captured asynchronously; the URL you get back might not have its assets fully captured for hours.

## Cross-References

- This skill populates the `archive_url` column described in `building-evidence-ledger`.
- For social-media items, also see `geolocating-imagery` if the post contains photos / video that need verification.
- For foreign-language pages, archive **before** translating — the snapshot is of the original; the translation is downstream.
