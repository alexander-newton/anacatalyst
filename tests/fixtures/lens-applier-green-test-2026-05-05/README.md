# lens-applier GREEN test — 2026-05-05

Output produced by the GREEN test of the `lens-applier` agent specification.

**Test scenario:** apply the public-finance lens to the Argentina capital-surcharge event (same seed as the `/strategic-brief` GREEN test, with the orchestrator's existing evidence ledger handed to the agent as input).

## What the test was checking

1. Does the agent produce the **exact 10-section output structure** the spec mandates?
2. Does it **stay in lane** — apply only public-finance frameworks, route political/historical/economic-microstructure questions out under "What this lens does not address"?
3. Does it **name canonical frameworks** from the lens skill rather than improvising?
4. Does it **calibrate probability and confidence separately**?
5. Does it **read and respect the existing evidence ledger** rather than duplicating verification?
6. Does it acknowledge tool-block honestly?

## Result

All six checks passed. Notable behaviours:

- **Conditional structure preserved.** Every probability is prefixed "conditional on the event being as described" — the agent did not collapse the F6 seed into a single point estimate. This is the hardest discipline to enforce and the spec elicited it.
- **Five sub-probabilities, not one.** The agent decomposed the call into brecha, spreads, rating action, default, and IMF friction — each with its own band. This is more useful to a synthesiser than a single number.
- **Frameworks named explicitly.** Original sin / currency-mismatch, debt-accumulation identity (with the algebra), Cole-Kehoe self-fulfilling rollover. All from the public-finance lens skill's framework list.
- **Lane discipline.** The "What this lens does not address" routes politics, microstructure, and geopolitical-signalling out cleanly. No drift.

## Structural finding (recurring)

The same WebFetch tool-block surfaced in this test as in the `/strategic-brief` and `building-evidence-ledger` GREEN tests. The lens-applier handled it correctly (acknowledged in the citations block, propagated to confidence). When this agent is registered as a real Claude Code subagent (not invoked via a `general-purpose` shim), the `tools` field in its frontmatter explicitly grants `WebFetch`, which should resolve the gap in production.

This fixture is a regression baseline: the spec should continue to produce comparably-structured, lane-disciplined output on similar pressure scenarios. If a future re-run drifts (e.g., starts narrating political coalition arithmetic under the public-finance lens), the spec has regressed.
