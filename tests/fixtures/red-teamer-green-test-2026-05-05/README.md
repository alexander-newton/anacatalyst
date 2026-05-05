# red-teamer GREEN test — 2026-05-05

Output produced by the GREEN test of the `red-teamer` agent specification, after one REFACTOR cycle.

**Test scenario:** independently red-team the Argentina capital-surcharge assessment, with the in-thread §9 red-team review *available but unread* until after producing a fresh review. Compare independent vs in-thread.

## What the test was checking

1. **Output discipline:** does the agent produce the full 9-section structured block, or compress everything into a comparison summary?
2. **Independence property:** does the independent red-team materially differ from the in-thread §9 — i.e., is the structural-independence argument for spinning up a separate agent actually justified?
3. **Methodology compliance:** all five canonical techniques (KAC, QoIC, ACH, Pre-mortem, Devil's Advocacy) applied, with substantive findings rather than ritual?
4. **Calibration discipline:** does the agent move the bands at the spec's default 5+pp expectation, with reasoning?

## Round 1 (RED — found a loophole)

First GREEN attempt produced strong substantive findings (3 specific places where §9 was calibration-soft, including the "theatre" diagnosis on KJ-3) but **collapsed the entire 9-section block into a comparison-only summary**. The response began with "Agreement." instead of `## Red-team review`. An orchestrator parsing by section heading would have seen no findings.

Cost: 38k tokens, 4 tool uses, 88s.

## REFACTOR

Two additions to the spec:
- An explicit "Your entire response IS the structured block" rule under section 5 of the workflow, with a "stop and start over" instruction if the agent finds itself paraphrasing.
- A new "Output-format red flags" section listing specific failure modes (begins with "Agreement.", "Summary:", "Here are my findings:"; fewer than 8 subsections; compresses required sections into Comparison; paraphrases structure rather than reproducing headings verbatim).

## Round 2 (GREEN — passed)

Re-test with updated spec produced the full structured block (this fixture). The substantive quality also *improved*:

- 7 KAC items (vs 3 implicit in round 1), including 3 new flags (translation ambiguity on "surcharge" → recargo/percepción/alícuota/cupo; "desperation" baked into H1 base case; >80% trigger claim asserted from pattern-matching not data)
- QoIC downgrades a *specific* judgement (KJ-2 trigger claim, B2 → C3) — the spec's "no-movement red-team is suspect" rule held
- ACH surfaces a *fourth* hypothesis the original H1/H2/H3 set missed: the announcement is a *negotiating posture* aimed at the IMF/bilateral counterparties, predicting the *opposite* of KJ-3
- Calibration moves more aggressively than §9: KJ-4 re-centred 60–80% → 45–65% (15pp shift), where §9 had only widened the lower bound by 5pp
- 5 new indicators with thresholds and time horizons, including a wire-desk-count diagnostic

Cost: 31k tokens, 3 tool uses, 81s. Token cost down, tool uses down, output quality up — the structured-output discipline focused the agent rather than constraining it.

## Why this matters — the structural-independence argument

The independent red-teamer found three things the in-thread §9 missed:
1. The negotiating-gambit hypothesis (not in H1/H2/H3, materially shifts KJ-3 direction)
2. A specific evidence downgrade (KJ-2 from B2 to C3)
3. Three new diagnostic indicators (AFIP-only publication, Treasury statement, volume-vs-price)

And it pushed the calibration further (15pp re-centring vs 5pp widening). This is exactly the kind of finding an in-thread red-team cannot produce because the drafter has skin in the game on the specific bands. The structural independence justifies the agent design.

This fixture is the regression baseline for the red-teamer agent. Future re-runs on comparable assessment + in-thread red-team pairs should produce comparably-structured output and find at least one substantive thing the in-thread review missed.
