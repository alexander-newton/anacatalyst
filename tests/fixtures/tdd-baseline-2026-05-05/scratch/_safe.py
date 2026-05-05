"""Shared credential-safety helpers for the integration test fetchers.

Implements the redaction patterns from skills/handling-credentials-safely/SKILL.md.
Never prints API key values; only proves presence via length.
"""
from __future__ import annotations

import os
import re
import sys
import time
from typing import Optional

import httpx
from dotenv import load_dotenv

# Always load .env once on import; values land in os.environ but are never printed.
load_dotenv(dotenv_path=os.path.join(
    os.path.dirname(__file__), "..", "..", ".env"
))

_SECRET_QS_RE = re.compile(
    r'((?:api[_-]?key|key|token|access_token|appkey|subscription[_-]?key|auth)=)[^&\s]+',
    flags=re.IGNORECASE,
)


def redact_url(url: str) -> str:
    """Replace any query-string secret value with <redacted>."""
    return _SECRET_QS_RE.sub(r'\1<redacted>', str(url))


def assert_key(name: str) -> str:
    """Confirm the named env var is present; return value (never print it)."""
    val = os.environ.get(name, "")
    if not val:
        raise RuntimeError(f"{name} missing from environment")
    print(f"[creds] {name} loaded, length={len(val)}", file=sys.stderr)
    return val


def safe_get(url: str, *, client: Optional[httpx.Client] = None,
             tries: int = 3, backoff: float = 1.0, **kwargs) -> httpx.Response:
    """GET with URL redaction on errors and exponential backoff."""
    last_exc = None
    for attempt in range(tries):
        try:
            if client is not None:
                r = client.get(url, **kwargs)
            else:
                r = httpx.get(url, **kwargs)
            r.raise_for_status()
            return r
        except httpx.HTTPStatusError as e:
            sanitised = redact_url(e.request.url)
            last_exc = httpx.HTTPStatusError(
                f"{e.response.status_code} for {sanitised}",
                request=e.request, response=e.response,
            )
            # 4xx auth errors won't get better with retries
            if 400 <= e.response.status_code < 500 and e.response.status_code not in (408, 429):
                raise last_exc from None
        except (httpx.HTTPError, httpx.TimeoutException) as e:
            req_url = getattr(getattr(e, "request", None), "url", url)
            last_exc = type(e)(f"{e.__class__.__name__} for {redact_url(req_url)}")
        if attempt < tries - 1:
            time.sleep(backoff * (3 ** attempt))
    raise last_exc  # type: ignore[misc]


def safe_post(url: str, *, tries: int = 3, backoff: float = 1.0, **kwargs) -> httpx.Response:
    last_exc = None
    for attempt in range(tries):
        try:
            r = httpx.post(url, **kwargs)
            r.raise_for_status()
            return r
        except httpx.HTTPStatusError as e:
            sanitised = redact_url(e.request.url)
            last_exc = httpx.HTTPStatusError(
                f"{e.response.status_code} for {sanitised}",
                request=e.request, response=e.response,
            )
            if 400 <= e.response.status_code < 500 and e.response.status_code not in (408, 429):
                raise last_exc from None
        except (httpx.HTTPError, httpx.TimeoutException) as e:
            req_url = getattr(getattr(e, "request", None), "url", url)
            last_exc = type(e)(f"{e.__class__.__name__} for {redact_url(req_url)}")
        if attempt < tries - 1:
            time.sleep(backoff * (3 ** attempt))
    raise last_exc  # type: ignore[misc]
