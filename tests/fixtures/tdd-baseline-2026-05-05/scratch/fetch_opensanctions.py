"""Cross-check shadow-fleet vessels via OpenSanctions /match/sanctions.

Per skills/fetching-ofac-sanctions/SKILL.md and skills/handling-credentials-safely/SKILL.md.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from _safe import assert_key, safe_post

OUT = Path(__file__).resolve().parent.parent.parent / "cache" / "opensanctions"
OUT.mkdir(parents=True, exist_ok=True)


def os_match(name: str, schema: str = "Vessel") -> dict:
    key = assert_key("OPENSANCTIONS_KEY")
    headers = {
        "User-Agent": "strategic-analyst/0.1 integration-test",
        "Authorization": f"ApiKey {key}",
    }
    payload = {"queries": {"q1": {"schema": schema, "properties": {"name": [name]}}}}
    r = safe_post("https://api.opensanctions.org/match/sanctions",
                  json=payload, headers=headers, timeout=30)
    return r.json()


def main() -> int:
    # Probe with a generic search via /search/default for the Russia shadow-fleet topic
    key = assert_key("OPENSANCTIONS_KEY")
    headers = {
        "User-Agent": "strategic-analyst/0.1 integration-test",
        "Authorization": f"ApiKey {key}",
    }
    import httpx

    # 1. List recent Vessel entities tied to the OFAC SDN dataset
    try:
        r = httpx.get(
            "https://api.opensanctions.org/search/sanctions",
            params={
                "schema": "Vessel",
                "countries": "ru",
                "limit": 50,
            },
            headers=headers,
            timeout=30,
        )
        r.raise_for_status()
        j = r.json()
        results = j.get("results", [])
        print(f"[opensanctions] Russian-flagged Vessel entities on sanctions: {j.get('total', {}).get('value', '?')}",
              file=sys.stderr)
        import json as _json
        (OUT / "russia_vessels.json").write_text(_json.dumps(j, indent=2))
        for v in results[:25]:
            caption = v.get("caption", "?")
            datasets = v.get("datasets", [])
            print(f"  - {caption} | datasets={datasets[:5]}", file=sys.stderr)
    except Exception as e:
        from _safe import redact_url
        msg = str(e)
        msg_redacted = redact_url(msg)
        print(f"[opensanctions] vessel listing errored: {type(e).__name__}: {msg_redacted}",
              file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
