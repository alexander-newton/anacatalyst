# source-ingestor GREEN test — 2026-05-05

Output produced by the GREEN test of the `source-ingestor` agent specification.

**Test scenario:** ingest 12 simulated GDELT items + 1 TCMB primary URL on a Turkey CBRT rate decision. The 12 items are designed to exercise the agent's hardest discipline rules:

- 6 of the 12 are a single Reuters wire republished across different country domains — must collapse to ONE ledger row.
- 1 X post claims a contradicting figure (350bp vs 250bp) — must be capped at D-grade.
- 1 Hurriyet item is Turkish-language — must flag translation drift.
- 1 WSJ item cites "unnamed sources" inside a B-grade outlet — info-grade should drop to 3 even though source-grade is B.
- 1 TCMB primary URL is supplied — must appear as a separate A-grade row even if not fetched.

## What the test was checking

1. **Format discipline** (carried forward from red-teamer REFACTOR): does the agent produce the full 7-section structured block, beginning with `## Source ingestion: <topic>`?
2. **Wire-collapse rule:** do the 6 Reuters republishers collapse to 1 ledger row attributed to the wire, with republisher count in `notes`?
3. **Anonymous-source capping:** is the X post graded D, with info-grade ≤ 3?
4. **Translation handling:** is the Hurriyet item flagged for translation drift?
5. **Anonymous-within-quality-outlet handling:** does the WSJ political-pressure claim cap at info-grade 3 despite source-grade B?
6. **Primary-source row:** is the TCMB URL emitted as a separate A-graded row even when not fetched?
7. **No body-text leakage:** zero quoted article body content?

## Result

All 7 checks passed first time, no REFACTOR needed. Cost: 28k tokens, 3 tool uses, 62s.

Notable behaviours that *exceeded* the spec:
- The X post was downgraded to info-grade 4 (not 3) because it directly contradicts convergent B-grade reporting. The spec only required D3.
- FT carries two items (political-framing + lira-move). The agent refused to count the political-framing item as independent corroboration of WSJ's political-pressure claim, even though both are FT/B-grade — recognising that editorial framing doesn't add independence.
- "Surprise" framing in Bloomberg/FT was flagged as not-independently-sourced to a consensus poll within the artlist — a finer distinction than the spec demanded.

## Carried-forward lesson

The "your entire response IS the structured block" rule, originally added in the red-teamer REFACTOR cycle, transferred cleanly to this spec. The source-ingestor passed format-discipline first time. This appears to be a generalisable pattern: structured-output specs need an explicit response-shape rule with named failure modes, or they degrade into summary substitution under load.

## Cosmetic finding (not REFACTOR-worthy)

The source-country distribution in Narrative 1 has duplicate keys (`{GB: 1, GB(FT): 1, GB(FT lira): 1}`) — should canonically aggregate to `{GB: 3, …}`. Future spec revision could require ISO-3166 alpha-2 codes only, but it's notation polish, not a discipline failure.

This fixture is the regression baseline. Future re-runs on comparable simulated artlists should produce comparably-structured output, with the wire collapse and grading rules applying identically.
