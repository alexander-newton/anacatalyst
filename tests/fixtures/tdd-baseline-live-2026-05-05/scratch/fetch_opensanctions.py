"""Cross-check sample Russia-shadow-fleet entities against OpenSanctions.

Documented in skills/fetching-ofac-sanctions/SKILL.md (Section 5: OpenSanctions).
"""
from __future__ import annotations
import os
import sys
import json
import datetime as dt
from pathlib import Path

import httpx
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent))
from _safe import safe_post, confirm_key  # noqa: E402

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

OUT = Path(__file__).resolve().parents[2] / "cache" / "opensanctions"
OUT.mkdir(parents=True, exist_ok=True)

KEY = os.environ.get("OPENSANCTIONS_KEY", "")
HEADERS = {"User-Agent": "strategic-analyst/0.1 (test)"}
if KEY:
    HEADERS["Authorization"] = f"ApiKey {KEY}"


def match(name: str, schema: str = "Vessel") -> dict:
    payload = {"queries": {"q1": {"schema": schema, "properties": {"name": [name]}}}}
    r = safe_post(
        "https://api.opensanctions.org/match/sanctions",
        json=payload,
        headers=HEADERS,
        timeout=30,
    )
    return r.json()


def main():
    confirm_key("OPENSANCTIONS_KEY", KEY)
    targets = [
        ("Sovcomflot", "Company"),
        ("Sun Ship Management", "Company"),
        ("Ingosstrakh", "Company"),
    ]
    summary = {"accessed_at": dt.datetime.now(dt.timezone.utc).isoformat(), "queries": []}
    for name, schema in targets:
        try:
            res = match(name, schema)
            results = res.get("responses", {}).get("q1", {}).get("results", [])
            print(f"\n{name} ({schema}): {len(results)} match(es)")
            for r in results[:5]:
                topics = r.get("properties", {}).get("topics", [])
                print(f"  - id={r.get('id')} score={r.get('score'):.2f} caption={r.get('caption')} topics={topics}")
            summary["queries"].append({
                "name": name, "schema": schema,
                "match_count": len(results),
                "top": [
                    {"id": r.get("id"), "score": r.get("score"),
                     "caption": r.get("caption"),
                     "topics": r.get("properties", {}).get("topics", []),
                     "datasets": r.get("datasets", [])}
                    for r in results[:3]
                ],
            })
        except Exception as e:
            print(f"{name} match failed: {type(e).__name__}: {str(e)[:200]}")
            summary["queries"].append({"name": name, "error": f"{type(e).__name__}: {str(e)[:200]}"})

    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, default=str))
    print(f"\nsummary.json saved")


if __name__ == "__main__":
    main()
