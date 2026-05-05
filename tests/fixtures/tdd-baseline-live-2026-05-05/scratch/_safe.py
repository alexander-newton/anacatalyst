"""URL/credential redaction helpers — applied in every fetcher per handling-credentials-safely."""
from __future__ import annotations
import re
import httpx


_SECRET_PATTERN = re.compile(
    r'((?:api_key|key|token|access_token|appkey|subscription-key|api-key)=)[^&\s]+',
    re.IGNORECASE,
)


def redact_query_secrets(url: str) -> str:
    return _SECRET_PATTERN.sub(r'\1<redacted>', url)


def safe_get(url: str, **kwargs) -> httpx.Response:
    """httpx.get with raise_for_status and URL-redaction in any raised error."""
    try:
        r = httpx.get(url, **kwargs)
        r.raise_for_status()
        return r
    except httpx.HTTPStatusError as e:
        sanitised = redact_query_secrets(str(e.request.url))
        raise httpx.HTTPStatusError(
            f"{e.response.status_code} for {sanitised}",
            request=e.request,
            response=e.response,
        ) from None
    except httpx.RequestError as e:
        sanitised = redact_query_secrets(str(getattr(e, "request", url)))
        raise httpx.RequestError(f"{type(e).__name__} for {sanitised}") from None


def safe_post(url: str, **kwargs) -> httpx.Response:
    try:
        r = httpx.post(url, **kwargs)
        r.raise_for_status()
        return r
    except httpx.HTTPStatusError as e:
        sanitised = redact_query_secrets(str(e.request.url))
        raise httpx.HTTPStatusError(
            f"{e.response.status_code} for {sanitised}",
            request=e.request,
            response=e.response,
        ) from None


def confirm_key(name: str, value: str | None) -> None:
    """Confirm a credential is set, by length only — never echo the value."""
    if not value:
        raise SystemExit(f"{name} missing from environment")
    print(f"{name} loaded, length={len(value)}")
