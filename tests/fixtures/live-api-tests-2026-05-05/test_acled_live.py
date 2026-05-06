"""Live API test for fetching-acled-events skill (2026 OAuth migration).

Three-step structure mirroring tests/fixtures/live-api-tests-2026-05-05/test_*_live.py:

  1. OAuth password grant against acleddata.com/oauth/token
  2. Authenticated read of Sudan events for the last 7 days
  3. Refresh-token round-trip (skipped if step 1 didn't return a refresh_token)

Per handling-credentials-safely:
  - Print credential PRESENCE only (length); never values.
  - Sanitise URLs in error messages.
  - NEVER include the token-endpoint response body in any error path —
    a 4xx response can echo the submitted password.
  - Never include the bearer token value in stdout.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import pathlib
import re
import sys
import time

import httpx

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
    """Strip credential-shaped substrings from any text intended for stdout."""
    s = re.sub(r"(password=)[^&\s\"]+", r"\1<redacted>", s, flags=re.IGNORECASE)
    s = re.sub(r"(refresh_token=)[^&\s\"]+", r"\1<redacted>", s, flags=re.IGNORECASE)
    s = re.sub(r"Bearer\s+\S+", "Bearer <redacted>", s, flags=re.IGNORECASE)
    return s


def safe_post_token(data: dict) -> dict:
    """POST to the token endpoint; never relay the response body on error.

    A 4xx body can include the submitted password verbatim.
    """
    try:
        r = httpx.post(
            "https://acleddata.com/oauth/token",
            data=data,
            timeout=30,
            headers={"User-Agent": "strategic-analyst-test/0.1"},
        )
        r.raise_for_status()
        return r.json()
    except httpx.HTTPStatusError as e:
        raise RuntimeError(
            f"token endpoint -> {e.response.status_code} (body suppressed; may echo password)"
        ) from None


def main() -> int:
    load_env()

    email = os.environ.get("ACLED_EMAIL", "")
    password = os.environ.get("ACLED_PASSWORD", "")
    assert email and password, "ACLED_EMAIL and ACLED_PASSWORD required in .env"
    print(f"[env] ACLED_EMAIL    loaded, length={len(email)}")
    print(f"[env] ACLED_PASSWORD loaded, length={len(password)}")

    summary: dict[str, object] = {}

    # ------------------------------------------------------------------
    # 1. password grant
    # ------------------------------------------------------------------
    print("\n=== 1. password grant against acleddata.com/oauth/token ===")
    t0 = time.time()
    try:
        tok = safe_post_token(
            {
                "grant_type": "password",
                "client_id":  "acled",
                "scope":      "authenticated",
                "username":   email,
                "password":   password,
            }
        )
    except RuntimeError as e:
        print(f"  FAIL: {e}")
        summary["password_grant_ok"] = False
        print("\n=== summary ===")
        print(json.dumps(summary, indent=2))
        return 1

    print(f"  HTTP 200 in {time.time() - t0:.2f}s")
    print(f"  response keys: {sorted(tok.keys())}")
    print(f"  token_type:    {tok.get('token_type')}")
    print(f"  expires_in:    {tok.get('expires_in')}s")
    print(f"  access_token  length={len(tok['access_token'])}")
    print(f"  refresh_token length={len(tok.get('refresh_token', ''))}")
    summary["password_grant_ok"] = True
    summary["has_refresh_token"] = bool(tok.get("refresh_token"))

    # ------------------------------------------------------------------
    # 2. authenticated read
    #
    # Window: ends 14 months ago, lasts 30 days. ACLED free-tier accounts
    # have a 12-month publication-lag restriction; querying inside the
    # restriction returns 0 rows even when events exist. This window is
    # well outside the restriction so the schema check actually fires.
    # ------------------------------------------------------------------
    print("\n=== 2. authenticated read (Sudan, 14-13 months ago) ===")
    end = dt.date.today() - dt.timedelta(days=14 * 30)
    start = end - dt.timedelta(days=30)
    t0 = time.time()
    try:
        r = httpx.get(
            "https://acleddata.com/api/acled/read",
            params={
                "country": "Sudan",
                "event_date": f"{start}|{end}",
                "event_date_where": "BETWEEN",
                "limit": 100,
            },
            headers={
                "Authorization": f"Bearer {tok['access_token']}",
                "User-Agent": "strategic-analyst-test/0.1",
            },
            timeout=30,
        )
        r.raise_for_status()
    except httpx.HTTPStatusError as e:
        url = redact(str(e.request.url))
        print(f"  FAIL: HTTP {e.response.status_code} for {url}")
        summary["read_ok"] = False
        print("\n=== summary ===")
        print(json.dumps(summary, indent=2))
        return 1

    payload = r.json()
    data = payload.get("data", [])
    print(f"  HTTP {r.status_code} in {time.time() - t0:.2f}s, body bytes={len(r.content)}")
    print(f"  rows: {len(data)}")

    if data:
        cols = sorted(data[0].keys())
        expected = {"event_id_cnty", "event_date", "event_type", "country", "fatalities"}
        missing = expected - set(cols)
        print(f"  schema check (expected cols present): missing={sorted(missing) or 'none'}")
        sample = data[0]
        print(
            f"  sample row: date={sample.get('event_date')}, "
            f"type={sample.get('event_type')}, "
            f"actor1={(sample.get('actor1') or '')[:40]}"
        )
        summary["read_rows"] = len(data)
        summary["schema_ok"] = not missing
    else:
        print("  (no rows in window — acceptable; widen if zero is unexpected)")
        summary["read_rows"] = 0
        summary["schema_ok"] = None
    summary["read_ok"] = True

    # ------------------------------------------------------------------
    # 3. refresh-token round-trip
    # ------------------------------------------------------------------
    print("\n=== 3. refresh-token round-trip ===")
    if tok.get("refresh_token"):
        t0 = time.time()
        try:
            fresh = safe_post_token(
                {
                    "grant_type":    "refresh_token",
                    "client_id":     "acled",
                    "refresh_token": tok["refresh_token"],
                }
            )
        except RuntimeError as e:
            print(f"  FAIL: {e}")
            summary["refresh_ok"] = False
        else:
            print(f"  HTTP 200 in {time.time() - t0:.2f}s")
            print(f"  new access_token length={len(fresh['access_token'])}")
            print(
                f"  identical to previous? "
                f"{fresh['access_token'] == tok['access_token']}"
            )
            summary["refresh_ok"] = True
    else:
        print("  SKIP: token endpoint did not return a refresh_token")
        print("        (the skill's refresh-first branch is dead code — remove it)")
        summary["refresh_ok"] = None

    print("\n=== summary ===")
    print(json.dumps(summary, indent=2))
    return 0 if summary.get("password_grant_ok") and summary.get("read_ok") else 1


if __name__ == "__main__":
    sys.exit(main())
