# GREEN test fixtures — 2026-05-05

Output produced by the GREEN test of `building-evidence-ledger` against the Turkey CBRT pressure scenario.

The skill's RED phase ran the same scenario without `building-evidence-ledger` loaded. The agent produced an inline markdown table and explicitly punted the primary fetch ("not opened tcmb.gov.tr — this is the next action"). The GREEN phase added the skill, ran the same scenario, and produced these two files:

- `turkey-cbrt-one-pager-2026-05-05.md` — the briefing one-pager. Includes a "Verification gap (state out loud)" section that explicitly distinguishes "tooling gap" from "analytical choice".
- `turkey-cbrt-rate-decision-2026-05-05.csv` — the structured ledger with one row per load-bearing claim, Admiralty-graded, including a row for the unfetched primary that records `ATTEMPTED FETCH at 08:25 BLOCKED by tooling permissions` rather than `not located`.

These are kept as regression fixtures: future re-runs of the same pressure scenario should produce comparably-structured output. If they don't, the skill has regressed (or the test scenario has drifted).

Pressure scenario: see the prompt in conversation history of 2026-05-05; reproduce by dispatching a `general-purpose` subagent with the strategic-news-analysis + building-evidence-ledger skills loaded, the Turkey 250bp/350bp three-source dilemma, and a 12-minute deadline.
