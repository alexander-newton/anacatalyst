# TDD baseline pass — 2026-05-05

Final integration test of the strategic-analyst plugin: full `/strategic-brief` workflow, dispatched as a single subagent with all skills + agents + live API keys available.

**Topic:** Recent OFAC designations targeting Russia's shadow-fleet oil tankers — scope, effectiveness, second-order EU energy-security impacts.

**Why this topic:** chosen specifically to stress the broadest cross-section of the suite: OFAC SDN, OpenSanctions, EIA (oil), FRED (macro), Comtrade (bilateral fuel flows), GDELT (narrative). Different shape from the prior Argentina (sovereign-debt) and Turkey (monetary-policy) fixtures so the test exercises the system rather than overfitting.

## What ran

The subagent's harness denied **Bash, WebFetch, and WebSearch** — the recurring sandbox constraint observed across seven prior tests. Despite this, the workflow produced a structurally sound deliverable rather than fabricating live data.

| Component | Outcome |
|---|---|
| Skill orchestration | ✅ Triaged 4 lenses (economic, geographic, political, military) of 7; left demographic / public-finance / historical out with reasoning |
| Evidence ledger | ✅ 17 rows, each `primary_url: not located (sandbox blocked)` honestly |
| Synthesis | ✅ BLUF + 4 KJs + lens ranking + verification gaps + indicators + separated confidence |
| Red-team | ✅ +5pp adjustment on revenue-compression KJ; 5 new indicators added; bottom-line direction held |
| Format compliance | ✅ DRAFT-WITH-MATERIAL-VERIFICATION-GAPS status declared at the top, not buried |
| Credential audit | ✅ **Clean** — no `*_KEY`, `*_TOKEN`, `*_SECRET` value appears in brief, ledger, or 8 scratch scripts |
| Runnable scripts produced | ✅ 8 scripts in `scratch/` ready to execute when sandbox permits |

## Files

- `russia-shadow-fleet-ofac-2026-05-05.md` (26KB) — the full BLUF brief with all 10 sections from `producing-deep-brief`
- `russia-shadow-fleet-ofac-2026-05-05.csv` (8KB) — 17-row evidence ledger
- `scratch/` — 8 runnable Python scripts the agent wrote per skill (`_safe.py` is the redaction helper used by all of them, `_smoke.py` is a one-line execution probe)

## Skill gaps surfaced (all applied to the suite this round)

1. **`fetching-fred-macro`** — TTF / NBP European gas benchmarks are *not* in FRED. Skill now flags this as a silent-substitution failure mode (the agent had used Henry Hub as a proxy without warning); also flags Russia-China bilateral flows + intraday data as out-of-scope.
2. **`handling-credentials-safely`** — assumed Python execution was always available. Skill now has a "When the sandbox denies execution entirely" section: don't claim keys are "loaded" if you couldn't call `os.environ`; mark every `primary_url: not located (sandbox blocked)`; emit `credential probe: not performed`.
3. **`/strategic-brief` command** — workflow assumed a working execution environment but had no graceful-degradation path. Command now has a step 0 pre-flight: probe `uv run python -c "import httpx"` + a network GET; if either fails, declare `SANDBOX-BLOCKED — all claims inference-graded` at the top of the brief instead of discovering the block fetcher-by-fetcher.

Net: the integration test exposed that the plugin's happy path depended on permissions the sandbox can withhold without warning. Fixes ship in this round; future re-runs against a permissive sandbox should reach live verification.

## Re-running

When sandbox permits Python execution:

```bash
# from the plugin root
uv run python tests/fixtures/tdd-baseline-2026-05-05/scratch/_smoke.py
uv run python tests/fixtures/tdd-baseline-2026-05-05/scratch/fetch_fred.py
# etc.
```

All scripts use the `_safe.py` redaction helper and confirm key presence by length only — they will not echo credential values even when run interactively.
