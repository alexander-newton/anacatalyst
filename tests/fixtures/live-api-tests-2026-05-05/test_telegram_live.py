"""Live test for fetching-telegram-channels skill.

Two parts:
  1. Unauthenticated HTML-mirror path against t.me/s/<channel> — no creds.
  2. Authenticated path: validate TELEGRAM_API_ID/HASH by *connecting* (not
     authorising). The connect step exercises the credentials at the MTProto
     handshake level without triggering the interactive phone-number prompt
     that the first authentication run would.

Applies the handling-credentials-safely discipline: confirm presence by length,
never echo values, sanitise URLs in errors.
"""
from __future__ import annotations

import asyncio
import os
import pathlib
import re
import sys
import time

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]


def load_env() -> None:
    for line in (PROJECT_ROOT / ".env").read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        v = v.strip().strip('"').strip("'")
        os.environ.setdefault(k, v)


def redact(s: str) -> str:
    s = re.sub(
        r'((?:api_key|client_secret|api_hash|access_token|token)=)[^&\s"]+',
        r"\1<redacted>",
        s,
        flags=re.IGNORECASE,
    )
    s = re.sub(r"Bearer\s+\S+", "Bearer <redacted>", s, flags=re.IGNORECASE)
    return s


# ---------------------------------------------------------------------------
# Part 1: unauthenticated HTML mirror
# ---------------------------------------------------------------------------
def test_html_mirror() -> None:
    import httpx
    from selectolax.parser import HTMLParser

    print("\n=== Part 1: unauthenticated t.me/s/ mirror ===")
    UA = "strategic-analyst/0.1 (research test)"
    # @telegram is the official Telegram News channel — stable, public, English.
    channel = "telegram"
    url = f"https://t.me/s/{channel}"

    t0 = time.time()
    try:
        r = httpx.get(url, headers={"User-Agent": UA}, timeout=30, follow_redirects=True)
        r.raise_for_status()
    except Exception as e:
        print(f"  FAIL: {redact(str(e))}")
        return

    elapsed = time.time() - t0
    print(f"  HTTP {r.status_code} in {elapsed:.2f}s, body {len(r.text)} bytes")

    tree = HTMLParser(r.text)
    posts = []
    for node in tree.css("div.tgme_widget_message")[-10:]:
        post_id_attr = node.attributes.get("data-post", "")
        msg_id = post_id_attr.split("/")[-1] if post_id_attr else None
        time_node = node.css_first("time.time")
        text_node = node.css_first("div.tgme_widget_message_text")
        view_node = node.css_first("span.tgme_widget_message_views")
        posts.append(
            {
                "msg_id": msg_id,
                "url": f"https://t.me/{channel}/{msg_id}" if msg_id else None,
                "datetime": time_node.attributes.get("datetime") if time_node else None,
                "text_preview": (text_node.text(strip=True)[:80] if text_node else "")
                + ("…" if text_node and len(text_node.text(strip=True)) > 80 else ""),
                "views": view_node.text(strip=True) if view_node else None,
            }
        )

    print(f"  parsed {len(posts)} posts; showing 3 most recent:")
    for p in posts[-3:]:
        print(f"    [{p['datetime']}] views={p['views']} id={p['msg_id']}")
        print(f"      url: {p['url']}")
        print(f"      text: {p['text_preview']}")
    if not posts:
        print("  (no posts parsed — selectors may have drifted on t.me)")
    return posts


# ---------------------------------------------------------------------------
# Part 2: authenticated path — credentials validation only (no interactive auth)
# ---------------------------------------------------------------------------
async def _telethon_connect_probe() -> dict:
    """Connect to MTProto using API_ID/HASH; do NOT call client.start().

    This validates that the credentials authenticate the *application* at the
    DC handshake; it does NOT authenticate a user (that needs an SMS code).
    """
    from telethon import TelegramClient

    api_id_raw = os.environ.get("TELEGRAM_API_ID", "")
    api_hash = os.environ.get("TELEGRAM_API_HASH", "")
    if not api_id_raw or not api_hash:
        return {"ok": False, "error": "credentials missing in .env"}

    if not api_id_raw.isdigit():
        return {"ok": False, "error": "TELEGRAM_API_ID is not numeric"}
    api_id = int(api_id_raw)

    if not re.fullmatch(r"[a-fA-F0-9]{32}", api_hash):
        return {
            "ok": False,
            "error": f"TELEGRAM_API_HASH shape: length={len(api_hash)}, expected 32 hex chars",
        }

    print(f"  TELEGRAM_API_ID:   numeric, length={len(api_id_raw)}")
    print(f"  TELEGRAM_API_HASH: hex, length={len(api_hash)}")

    # Use an in-memory session so no .session file is written and we don't
    # accidentally bind a user account during this probe.
    from telethon.sessions import MemorySession

    client = TelegramClient(MemorySession(), api_id, api_hash)
    try:
        await client.connect()
        is_authorised = await client.is_user_authorized()
        # Read DC from the underlying connection if available.
        dc_id = getattr(client.session, "dc_id", None)
        await client.disconnect()
        return {
            "ok": True,
            "is_user_authorised": is_authorised,
            "dc_id": dc_id,
        }
    except Exception as e:
        try:
            await client.disconnect()
        except Exception:
            pass
        return {"ok": False, "error": redact(f"{type(e).__name__}: {e}")}


def test_telethon_creds() -> None:
    print("\n=== Part 2: telethon credentials validation (connect only, no auth) ===")
    result = asyncio.run(_telethon_connect_probe())
    if result.get("ok"):
        print(
            f"  HANDSHAKE OK: connected to DC {result.get('dc_id')}, "
            f"is_user_authorised={result.get('is_user_authorised')}"
        )
        if not result["is_user_authorised"]:
            print(
                "  (expected: no .session yet — the first authenticated run will "
                "prompt for a phone number, then an SMS code)"
            )
    else:
        print(f"  FAIL: {result.get('error')}")


def main() -> int:
    load_env()
    print("Telegram skill live test — applying handling-credentials-safely")
    posts = test_html_mirror() or []
    test_telethon_creds()

    print("\n=== summary ===")
    print(f"  unauth HTML mirror: {'OK' if posts else 'FAIL'} ({len(posts)} posts)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
