---
name: handling-credentials-safely
description: Use whenever an API key, token, or other credential is being loaded or used — by a fetch skill, a lens-applier or source-ingestor agent, a one-off script, or any code path that reaches an authenticated endpoint. Triggers include "use the API key", any os.environ load of a *_KEY / *_TOKEN / *_PASS / *_SECRET variable, any HTTP request that includes credentials, and any subagent invocation that has access to .env.
---

# Handling Credentials Safely

## Overview

API keys leak through three predictable channels: **printed verbatim** in summary output, **echoed in error tracebacks** that include the request URL, and **embedded in cache file names or paths**. All three were observed in the live test of 2026-05-05 — the FRED key appeared in an httpx 5xx traceback, and the EIA key was printed verbatim by an agent in its final summary back to the orchestrator. The skill is the discipline that keeps the value in memory and out of the visible stream.

**Core principle:** *The key is for the request, not for the report.* The orchestrator that invoked you, the user reading your output, and any future log file should never see the raw bytes of a credential. They see "key present, length 32" or nothing at all.

## When to Use

- Loading any `*_KEY`, `*_TOKEN`, `*_PASS`, `*_SECRET` from `.env` or the environment.
- Building HTTP requests that include credentials.
- Catching exceptions from authenticated requests.
- Producing a summary or report that touches a fetch.
- Writing cache files for an authenticated API.
- Dispatching a subagent that will touch any of the above.

**This skill applies even when "nobody is watching" — agent transcripts get logged, error tracebacks get pasted into bug reports, summaries become fixtures.** Treat the orchestrator and the future reader as untrusted.

## The Five Rules

### 1. Load via `os.environ`, never via `cat .env` or `Read`

```python
# Correct — loads the value into the running process, nothing printed
import os
from dotenv import load_dotenv
load_dotenv()
KEY = os.environ["FRED_API_KEY"]

# Wrong — `cat .env` echoes every key value into the agent's tool-result stream
# subprocess.run(["cat", ".env"])     # don't
# pathlib.Path(".env").read_text()    # don't, when followed by print(...)
```

Reading the .env file directly is *acceptable* if you immediately parse and assign to environment variables and **never print the file's contents**. The risk is the unconscious `print(env_text)` or returning the parsed dict from a function that gets logged.

### 2. Confirm presence by length, never by value

```python
# Correct — proves the key is set without exposing it
key = os.environ.get("FRED_API_KEY", "")
assert key, "FRED_API_KEY missing from environment"
print(f"FRED_API_KEY loaded, length={len(key)}")

# Wrong — leaks the key into output that may be logged or summarised
print(f"FRED_API_KEY loaded: {key}")           # don't
print(os.environ)                              # don't — dumps everything
print({k: v for k, v in os.environ.items()})   # don't, same thing
```

This is the most-common leak mode for agents writing summaries. Agents naturally want to "show their work" — the discipline is to show that the work *happened*, not the values that flowed through it.

### 3. Sanitise URLs in error handling

`httpx` and `requests` both include the full request URL in the message of a raised exception. For APIs that take credentials in the query string (FRED, EIA), this means the raw key shows up in any 5xx traceback. Wrap and re-raise:

```python
import re, httpx

def _redact_query_secrets(url: str) -> str:
    return re.sub(
        r'((?:api_key|key|token|access_token|appkey)=)[^&]+',
        r'\1<redacted>',
        url,
        flags=re.IGNORECASE,
    )

def safe_get(url: str, **kwargs) -> httpx.Response:
    try:
        r = httpx.get(url, **kwargs)
        r.raise_for_status()
        return r
    except httpx.HTTPStatusError as e:
        sanitised = _redact_query_secrets(str(e.request.url))
        raise httpx.HTTPStatusError(
            f"{e.response.status_code} for {sanitised}",
            request=e.request, response=e.response,
        ) from None
```

Use `safe_get` (or an equivalent client-level event hook) in every fetcher skill that puts credentials in the query string. APIs that accept `Authorization: Bearer ...` headers (OpenSanctions, DeepL, most modern APIs) avoid the problem entirely — prefer headers when both options exist.

### 4. Never put credentials in cache filenames or paths

```python
# Correct — hash the (query, dates, mode) tuple; the key is not part of the identity
key_hash = hashlib.sha256(f"{query}|{start}|{end}".encode()).hexdigest()[:16]
cache_path = pathlib.Path(f"cache/gdelt/{key_hash}.parquet")

# Wrong — even if the key is "just for this analyst", filenames end up in
# `git status`, `find` output, screenshots, and shell history.
# pathlib.Path(f"cache/fred/{API_KEY}-{series_id}.parquet")  # don't
```

The cache key should be the *content identity*, not the *credential identity*. Two analysts using different keys to fetch the same series should hit the same cache.

### 5. Sanitise summaries that are returned to the orchestrator

When an agent (lens-applier, source-ingestor, red-teamer, source-ingestor) returns a structured summary, audit it before sending. The discipline:

- Never include `os.environ.get("...")` results that resolve to credentials in any returned text.
- Never paste full URLs that include `api_key=...` into the summary.
- If you describe what you did, describe it as `"queried FRED with the configured API key"`, not `"queried https://api.stlouisfed.org/fred/...?api_key=xxxxxxxx..."`.
- If a request failed and you want to show the error, redact via `_redact_query_secrets` first.

## Cache-File Hygiene

Cache directories that contain authenticated-API responses should be `.gitignore`d. The data isn't the secret, but caches occasionally include response headers (which can echo back tokens or session IDs in some APIs). The strategic-analyst plugin's `.gitignore` already excludes `cache/`.

## Agent and Subagent Discipline

When you (the orchestrator) dispatch a `general-purpose`, `lens-applier`, `source-ingestor`, or `red-teamer` subagent:

- **Do not paste credential values into the subagent prompt.** Refer to the env var by name (`FRED_API_KEY`) and let the subagent load it from `.env` itself.
- **Tell the subagent explicitly to apply this skill** when its task involves an authenticated fetch. The cross-reference is `**REQUIRED:** Apply skills/handling-credentials-safely.`
- **Audit the subagent's returned summary.** If the response includes a credential value, do not relay it — flag the leak, treat the relevant key as compromised, and recommend rotation.

## Common Mistakes

| Mistake | Fix |
|---|---|
| `print(os.environ)` for "debugging" | Print specific keys' presence by length only, or use `pprint` with redaction. |
| Letting `httpx`'s default error message bubble up | Wrap in `safe_get`; sanitise the URL before re-raising. |
| Including the working API URL in agent reports | Describe the request in prose; don't paste the URL. |
| Storing the key in a function default argument | Defaults are read once at definition; use `os.environ` inside the function body. |
| Logging at DEBUG level in production-ish runs | DEBUG often dumps headers including `Authorization`. Use INFO or higher; configure the HTTP client to redact. |
| Echoing the key in the subagent test prompt | Reference by env var name; never paste the value. |
| Reading `.env` and printing the result | Parse and assign to `os.environ`; never `print` the parsed dict. |

## When the Sandbox Denies Execution Entirely

Sometimes the harness denies `Bash`, `WebFetch`, *and* `WebSearch` — the agent cannot run Python, cannot call `os.environ`, cannot fetch anything. This recurs in subagent contexts.

**The right response is to stop, not to switch into inference mode.**

A "DRAFT WITH MATERIAL VERIFICATION GAPS / all claims inference-graded" deliverable is *worse* than no deliverable. It produces a polished structured artefact (BLUF, ledger, key judgements with calibrated bands) whose verification caveats a downstream reader will forget while acting on the analysis. Hard-fail instead.

**The required behaviour when execution is denied:**

- **Refuse with one line.** Reply: `cannot continue: <execution|network|specific-key> denied/missing. Fix and re-run. No structured output produced.`
- **Do not produce a brief, ledger, sitrep, lens-finding, or synthesis** based on training-corpus knowledge.
- **Do not write any file** as a "what I would have done if I could" stub. Future re-runs will produce real output; speculative artefacts only confuse the regression suite.
- **Do not echo env-var names** as if they were values. Names plus the phrase "loaded" can mislead a reader into believing a probe happened.
- **Do not declare keys "loaded"** if you couldn't call `os.environ`. The honest output is `credential probe: not performed (execution denied)`.

This applies across `/strategic-brief`, `/daily-sitrep`, `/verify-claim`, the lens-applier and source-ingestor agents, and any fetch-dependent skill. **Exceptions:** purely analytical actions (red-teaming an *existing* assessment + ledger; format-only operations on already-fetched data) can proceed without a fetch probe — the dependency they have is the *artefact*, not the fetch capability.

The discipline is *honesty over polish*: a one-line refusal is a stronger artefact than a 26KB inference-grade brief.

## Recovery — When a Key Has Leaked

The leak is in two places: the live transcript / log, and the conversation context. Both are recoverable but the key itself must rotate:

1. **Rotate immediately.** All the keys this plugin uses are free-tier and instantly regenerable. Revoke the old key in the issuing portal; generate a new one.
2. **Update `.env`** with the new value. The SessionStart hook will confirm it on next session.
3. **Audit fixtures.** If a test fixture under `tests/fixtures/` contains a leaked key, redact and overwrite the file. Re-run the affected test with the new key.
4. **Note the leak in the relevant fixture's README** so future readers know the key in any prior version of the file is invalid.

## Cross-References

- `building-evidence-ledger` — when recording an authenticated fetch in the ledger's `notes`, describe the methodology without including the URL with embedded credentials. "Queried FRED for series CPIAUCSL, observation_start=2020-01-01" is correct; pasting the full URL is not.
- All fetcher skills (`fetching-fred-macro`, `fetching-eia-energy`, `fetching-acled-events`, `fetching-comtrade-trade`, `fetching-newsapi-articles` etc.) cross-reference this skill — apply the five rules whenever the skill's documented Python pattern includes an `api_key=` parameter.
- All agent specs (`agents/lens-applier.md`, `agents/source-ingestor.md`, `agents/red-teamer.md`) cross-reference this skill — the orchestrator depends on agent summaries staying clean.
