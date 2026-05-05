---
name: fetching-telegram-channels
description: Use when the analyst needs Telegram channel content — Russian milblogger reports, Iranian state and proxy channels, Sahel-conflict feeds, or any topic where mainstream media is absent or lagging. Triggers include "what is the milblogger saying", "Telegram channel X", "Russian-language report", front-line tempo, channel-level monitoring, and any verification of a claim that originates on Telegram.
---

# Fetching Telegram Channels

## Overview

For Russia-Ukraine, Iran and the broader Middle East, and increasingly the Sahel, **Telegram is the OSINT signal source** — Russian milbloggers post strikes hours before wire pickup; Iranian state and proxy channels publish official messaging in original Persian/Arabic; Sahel-conflict feeds run on Telegram because journalists can't operate on the ground. Mainstream media re-reports Telegram with delay and translation drift; the analyst goes upstream.

**Core principle:** *Telegram channels are sources, not stories.* A single milblogger post is a D-grade input regardless of follower count. The analyst's job is to grade the channel, grade the claim, and propagate the right info-grade — not to launder Telegram into "reports indicate".

## When to Use

- Tracking front-line tempo (Russia-Ukraine, Sudan, Yemen, Sahel) where Telegram outpaces wires.
- Reading **state and quasi-official messaging** in original language (Russian MFA, IRGC outlets, Hezbollah's Al-Manar, Houthi spokespeople, Tatmadaw channels).
- Spotting a claim that's circulating only on Telegram so far — it may break to wire in 6–24h, or it may be propaganda; either is useful.
- Verifying a media claim that says "according to Telegram channel X" — fetch the original post.
- Time-bounding a claim's emergence: when did this first appear?

**Skip for:**
- Stable structured data (use a real database).
- Topics already well-covered by wires within the time window.
- Closed channels you don't have access to. Do not impersonate to gain access.

## Two Access Paths

### A. Unauthenticated HTML mirror — `t.me/s/<channel>` (default for read-only browsing)

Telegram exposes a **public read-only mirror** at `https://t.me/s/<channel-name>` that renders the channel's recent posts as static HTML, **with no login or API key required**. This is the right default for ad-hoc verification of a single post or a quick scan.

```python
import httpx, re
from selectolax.parser import HTMLParser  # uv add selectolax

UA = "strategic-analyst/0.1 (+research; contact: <your-email>)"

def telegram_channel_html(channel: str, limit: int = 20) -> list[dict]:
    """Fetch the public HTML mirror of a Telegram channel.

    Returns a list of post dicts. Read-only; no auth.
    """
    r = httpx.get(f"https://t.me/s/{channel}", headers={"User-Agent": UA}, timeout=30)
    r.raise_for_status()
    tree = HTMLParser(r.text)
    posts = []
    for node in tree.css("div.tgme_widget_message")[-limit:]:
        post_id_attr = node.attributes.get("data-post", "")  # e.g. "channel/12345"
        msg_id = post_id_attr.split("/")[-1] if post_id_attr else None
        time_node = node.css_first("time.time")
        text_node = node.css_first("div.tgme_widget_message_text")
        view_node = node.css_first("span.tgme_widget_message_views")
        forward_node = node.css_first("a.tgme_widget_message_forwarded_from_name")
        posts.append({
            "msg_id": msg_id,
            "url": f"https://t.me/{channel}/{msg_id}" if msg_id else None,
            "datetime": time_node.attributes.get("datetime") if time_node else None,
            "text": text_node.text(strip=True) if text_node else "",
            "views": view_node.text(strip=True) if view_node else None,
            "forwarded_from": forward_node.text(strip=True) if forward_node else None,
        })
    return posts
```

**Strengths:** no setup, no rate limits worth worrying about for read scale, no app registration. Works for any *public* channel.

**Limits:** can't search history beyond what the page renders (~20 most recent posts), can't access private channels, can't filter by date window beyond client-side, no media-file download via this surface.

### B. Authenticated User API via `telethon` (for history search, larger windows, media)

For history beyond the most-recent-20 window, full-text search across a channel, or downloading media files, use the User API via the `telethon` library. Requires a free Telegram developer app.

**Setup:**

1. Register a developer app at [my.telegram.org/apps](https://my.telegram.org/apps) (one-time, ~3 min). You'll receive an `api_id` (numeric) and `api_hash` (32-char string).
2. Set in `.env`:
   ```
   TELEGRAM_API_ID=...
   TELEGRAM_API_HASH=...
   ```
3. First run will prompt for your phone number for authentication. The session is saved to a `.session` file (gitignore it).

```python
# uv add telethon
import os
from telethon.sync import TelegramClient

API_ID = int(os.environ["TELEGRAM_API_ID"])
API_HASH = os.environ["TELEGRAM_API_HASH"]

def telegram_channel_history(channel: str, limit: int = 200,
                              since: str | None = None,
                              query: str | None = None) -> list[dict]:
    """Fetch authenticated channel history with optional date pin and text query.

    `channel` is the @handle (without the @) or numeric channel ID.
    `since` is an ISO 8601 datetime; only posts on or after it are returned.
    `query` is a substring filter (server-side where supported).
    """
    import datetime as dt
    posts = []
    with TelegramClient("strategic-analyst", API_ID, API_HASH) as client:
        kwargs = {"limit": limit}
        if since:
            kwargs["offset_date"] = dt.datetime.fromisoformat(since.replace("Z", "+00:00"))
        if query:
            kwargs["search"] = query
        for msg in client.iter_messages(channel, **kwargs):
            posts.append({
                "msg_id": msg.id,
                "url": f"https://t.me/{channel}/{msg.id}",
                "datetime": msg.date.isoformat(),
                "text": (msg.text or "")[:1000],
                "views": getattr(msg, "views", None),
                "forwards": getattr(msg, "forwards", None),
                "has_media": bool(msg.media),
                "forwarded_from": getattr(msg.forward, "chat", None)
                                  and getattr(msg.forward.chat, "username", None),
            })
    return posts
```

**Strengths:** full history (subject to channel-level retention), text search, forward-graph access, media download.

**Limits:** rate-limited per account; aggressive use can trigger flood-wait. Authenticated session means your phone number is associated with the activity — keep that in mind for sensitive research.

## Channel Source-Grading

Telegram is **not one source**. Grade channel-by-channel:

| Channel type | Default source-grade | Notes |
|---|---|---|
| Official state ministry / regulator (`@MID_Russia`, `@CBR_official`, `@JCSWebsite`) | **A** for primary statements; **B** for editorial framing | These are primary documents. Cite as A1 when quoting an official statement; downgrade for derivative commentary. |
| Named state media with editorial board (`@TASSagency`, `@RT_com`, `@PressTV_irib`) | **B** | Read as "what this state wants known" — itself useful information. Not independent fact. |
| Named journalists / verified analysts (own name, recognised by mainstream outlets) | **B/C** | Verified-status alone doesn't move the grade; track record does. |
| Pseudonymous milbloggers / war-correspondents (Rybar, WarGonzo, Igor Strelkov) | **C/D** | Influential, often well-sourced, but anonymous. Cap at C3 unless corroborated by primary or A-grade. |
| Aggregator / forwarder bots | **D** | Republish without attribution. Useful for spotting; never source. |
| Anonymous "OSINT" channels with no track record | **D** | Treat as social media — D until proven otherwise. |
| Channels claiming to be official without independent verification | **F** | Impersonation is common. Check official websites for the channel link before grading. |

**Apply the channel grade as the row's `source_grade`. The info_grade still depends on the specific claim:** a B-grade state-media channel asserting "we won the war" is still info-grade 4–5; a D-grade milblogger reporting GPS coordinates of a strike that geolocates and matches commercial satellite imagery is info-grade 2.

## Verification Discipline (the special rules for Telegram)

1. **The post URL is canonical.** `https://t.me/<channel>/<msg_id>` is the citation. Forwarded posts have a different URL — record both the forward and the original.
2. **Archive immediately.** Telegram channels delete posts; some delete entire histories. Wayback's coverage of `t.me` is patchy because the page is JS-heavy; **`archive.today` works better for Telegram**. Pair this skill with `archiving-with-wayback` and explicitly try archive.today for Telegram URLs.
3. **Translate via the discipline.** Most channels are not English. Apply `translating-foreign-source`: cite the original-language post, name the translator, downgrade by one info-grade pending native-speaker review. The "false-corroboration via translation drift" failure mode is acute on Telegram because milbloggers often re-broadcast the same claim across language variants.
4. **Forwarding is not corroboration.** Channel A forwarding from Channel B is one source (B). Forwarding to many channels does not multiply independence. Track the *original*.
5. **Visual evidence requires geolocation.** Strike photos / video posted to milblogger channels are the analyst's most-common verification target. Pair with `geolocating-imagery` — reverse-search, sun position, terrain match, AI-generation check.
6. **Track by numeric channel ID, not handle.** Channels rename. The handle `@example_old` may be a different entity from `@example_new` even when both are claimed to be the same channel. The numeric ID is stable; record it.

## Common Mistakes

| Mistake | Fix |
|---|---|
| Citing "according to Telegram" without naming the channel | Name the channel and grade it. "Telegram" is not a source; specific channels are. |
| Treating follower count as a quality signal | Pseudonymous channels routinely have 500k+ followers and still cap at C/D. Grade by track record, not reach. |
| Counting a forwarded post as independent | One source per original post. Forwards are amplification, not corroboration. |
| Forgetting to archive before citing | Posts disappear faster than `t.me`'s mirror updates. Archive at moment of access, prefer archive.today over Wayback for Telegram. |
| Using machine-translated claim verbatim | Translation hazards on Russian/Persian/Arabic political vocabulary are severe. Apply `translating-foreign-source` for any load-bearing claim. |
| Treating "verified" status as a quality signal | Telegram has no widely-recognised verification scheme equivalent to X's blue check; the platform's own "Verified" mark applies sparsely. Grade by source-of-record, not platform metadata. |
| Logging in with your personal phone number for sensitive research | The User API binds activity to a phone number. Use a dedicated research number; treat the `.session` file as a credential and gitignore it. |
| Skipping the `t.me/s/` route and going straight to telethon | The HTML mirror handles 80% of analyst use cases without auth. Only escalate to authenticated API when you need history beyond 20 posts or full-text search. |

## Caching Pattern

```python
import pathlib, hashlib, json, time
CACHE = pathlib.Path("cache/telegram"); CACHE.mkdir(parents=True, exist_ok=True)

def cached_channel(channel: str, limit: int = 50, max_age_minutes: int = 30) -> list[dict]:
    """Cache the t.me/s/ HTML-derived feed by (channel, limit)."""
    key = hashlib.sha256(f"{channel}|{limit}".encode()).hexdigest()[:16]
    path = CACHE / f"{key}.json"
    if path.exists() and (time.time() - path.stat().st_mtime) / 60 < max_age_minutes:
        return json.loads(path.read_text())
    posts = telegram_channel_html(channel, limit=limit)
    path.write_text(json.dumps(posts, indent=2))
    return posts
```

For sensitive front-line tracking, drop `max_age_minutes` to 5; for state-media monitoring, 60 is fine.

## Polite Use

- **Identify your client** in the User-Agent for the HTML mirror.
- **Throttle**: ≤ 1 request per 4–5 seconds for sustained scraping. The HTML mirror is a Telegram-controlled surface — burst traffic gets you blocked.
- **Telethon flood-wait**: respect the API's `FloodWaitError` and back off.
- **Don't republish without attribution**. The channel's content is not yours; cite the post URL whenever you quote.

## Cross-References

- **REQUIRED: Apply `handling-credentials-safely`** when using the authenticated API. `TELEGRAM_API_HASH` and the saved `.session` file are credentials. Add `*.session` to `.gitignore`. Never echo the api_hash; confirm presence by length.
- **REQUIRED: Apply `translating-foreign-source`** for any non-English channel post that becomes a load-bearing claim.
- **Pair with `archiving-with-wayback`** — archive.today is usually the working path for Telegram URLs.
- **Pair with `geolocating-imagery`** for the verification chain on strike photos / video.
- Output rows feed `building-evidence-ledger` with the channel-by-channel grading above.
- For non-Telegram social-channel monitoring (X, Bluesky, Mastodon), use the search skill and the source hierarchy from `strategic-news-analysis`.
