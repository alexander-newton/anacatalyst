---
name: producing-deep-brief
description: Use when assembling the final deliverable of a strategic-news-analysis run into a BLUF-style decision-support brief, after lens analysis, synthesis, and red-team have completed. Triggers include "produce the brief", "write up the assessment", "format the output", "executive memo", and any case where multiple lens findings must be turned into a single decision-support document.
---

# Producing a Deep Brief

## Overview

A deep brief is the **canonical output format** of a `/strategic-brief` run. It encodes the discipline of the analytical workflow into a shape a principal can read in one pass and a colleague can audit in five minutes. The skill is the format itself — what goes where, what's required, what the section *means*.

**Core principle:** *The format is doing analytical work.* BLUF order forces the conclusion first; calibrated bands force probability separated from confidence; "what's established vs reported vs inferred" makes claim-strength visible at a glance. Departing from the format silently degrades all three.

## When to Use

- Producing the final deliverable from `/strategic-brief`.
- Writing up an ad-hoc deep dive that involves the lens stack and synthesis.
- Translating a synthesis-only product (from `synthesising-strategic-assessment`) into the standard hand-off format.

**Skip for:**
- Daily sweeps — use `producing-daily-sitrep`.
- Single-claim verifications — `verify-claim` produces its own one-row deliverable.
- Internal notes, exploratory work, or informal questions.

## The Format

A deep brief is a single markdown file at `briefs/<topic-slug>-<YYYY-MM-DD>.md`. Sections are required and ordered. Departing from the order is permitted only when a section is genuinely empty — and even then, "no findings under this lens" is a sentence, not a missing section.

```markdown
# <Topic>: <one-line angle>

**Decision-support brief — <YYYY-MM-DD>**
**Analyst:** <name or role>
**Status:** <DRAFT | FINAL | DRAFT WITH MATERIAL VERIFICATION GAPS>

---

## 1. Bottom Line Up Front

<One paragraph. The conclusion. Calibrated probability band, separated from confidence. If the bottom line depends on a conditional ("if the seed is real…"), the conditional is in the FIRST sentence, not buried.>

- **Probability the [event / outcome] holds:** <"likely (60–80%)" / "roughly even (45–55%)" / etc.>, **<low / moderate / high>** confidence.
- **Conditional probabilities** (where applicable, separated):
  - Within <horizon>: <claim> — <band>, **<confidence>**.
  - …

## 2. Key Judgements

Numbered, 2–5 of them. Each:

**KJ-1 — <one-line claim>.** *(Lens: <which one>. Reliability: <A/B/C>. Impact: <high/medium/low>.)*
<One short paragraph. The judgement. The evidence weight. The residual uncertainty.>

**KJ-2 — <…>.** *(Lens. Reliability. Impact.)*
<…>

## 3. Reasoning by lens

Lenses appear in **rank order of causal weight**, not as a checklist. Drop lenses that aren't doing causal work; "demographic — not load-bearing at this horizon" is one line, not a section.

### <Dominant lens — e.g. Public Finance>
<One paragraph or short bullets. Frameworks named. Which mechanism is operating. What it predicts. Citations to ledger rows.>

### <Secondary lens — e.g. Political>
<One paragraph. The binding-constraint pattern: "Politically the move is desirable for X; fiscally it is unaffordable without Y; the binding constraint is fiscal." Foreground disagreements rather than averaging them out.>

### <Background lenses listed but not expanded>
- Historical: <one line>
- Geographic: <one line>
- Demographic / Military: not load-bearing at this horizon.

## 4. What's established / reported / inferred

- **Established (A1/A2):** <bullet — primary documents and confirmed facts>
- **Reported (B2/C3):** <bullet — wire and analyst claims with their grades>
- **Inferred:** <bullet — analyst's deduction from the structural picture, distinguished from the above>

This section makes claim-strength visible at a glance. The reader should be able to tell which sentence is fact, which is claim, and which is the analyst's inference.

## 5. Verification gaps

Listed explicitly, not buried. Each gap is a thing the analyst tried to close and couldn't, with the consequence stated.

- <gap>: <why it matters; what would close it>
- <gap>: <…>

If the brief is `DRAFT WITH MATERIAL VERIFICATION GAPS`, the verification-gap list determines that status — not a footer caveat.

## 6. Indicators to watch

Concrete, observable, time-bound. Each indicator names a threshold and a horizon.

- <indicator>: threshold = <…>; horizon = <T+24h / T+7d / T+30d>; what it discriminates.
- <indicator>: <…>
- <indicator>: <…>

The brief converts an assessment into a *living product* through this section. Without it, the brief is a snapshot, not a forecast.

## 7. What would change the call

- **Reduce the call:** <named conditions that would lower the probability band>.
- **Reverse the call:** <conditions that would invert it>.
- **Escalate / increase exposure:** <conditions that would shift to a stronger judgement>.

## 8. Confidence

One short paragraph. State *separately* from probability. Confidence reflects evidence quality, quantity, and analytical disagreement — not the strength of the central claim. A "likely (65%)" judgement with low confidence is a different statement from "likely (65%)" with high confidence.

## 9. Red-team review

Inserted by the `/red-team` slash command or the `red-teamer` agent. If absent, the brief is `DRAFT`, not `FINAL`.

## 10. Sources

Reference to the evidence ledger: `evidence/<topic-slug>-<YYYY-MM-DD>.csv`. Inline list of the load-bearing primaries. Distinguish A-grade primaries from B-grade wires from C-grade analyst commentary.
```

A worked example is in the `tests/fixtures/strategic-brief-green-test-2026-05-05/` directory of this plugin.

## Quick Reference

| Element | Done well | Done badly |
|---|---|---|
| Bottom line | One paragraph, calibrated, falsifiable | "It's complicated"; "various factors"; uncalibrated |
| Probability + confidence | Stated separately | Conflated |
| Lens reasoning | Ranked by causal weight; dominant lens foregrounded | Seven equal-weight sections; reads like a checklist |
| Established / reported / inferred | One section, bullet-by-bullet | Buried in prose |
| Verification gaps | Section 5, explicit | Footer caveat |
| Indicators | Threshold + horizon + what it discriminates | Generic ("watch the situation") |
| Confidence | Section 8, separate from probability | Mixed into the band |
| Red-team | Section 9, post-hoc, materially moves the call | Absent or rubber-stamp |

## Common Mistakes

| Mistake | Fix |
|---|---|
| BLUF sentence is the headline, not the call | Rewrite as: claim, calibrated band, confidence — in that order. |
| Lens section reads as seven equal blocks | Rank by causal weight; demote non-load-bearing lenses to one-liners. |
| Verification gaps in a footer | Move to section 5 with explicit consequences. |
| Indicators are vague ("watch the lira") | Add a threshold (">4% intraday move"), a horizon ("T+24h"), and what it discriminates. |
| Confidence and probability conflated | Separate them: probability = "how likely", confidence = "how solid is the inference chain". |
| Red-team is rubber-stamp | If §9 doesn't move at least one band, it's not red-team — call it review. |
| "Sources: see ledger" with no inline cites | List the load-bearing primaries by name and grade; the ledger is the audit trail, not a substitute for citation. |
| The brief assumes its own seed | If the seed claim is itself unverified, that goes in §1 BLUF as the headline finding, not buried in §5. |

## Cross-References

- Synthesis-stage skill is `synthesising-strategic-assessment` — that skill produces the *content* of sections 1–8; this skill produces the *format*.
- The red-team in §9 is produced by `red-teaming-analysis` (skill) or the `red-teamer` agent.
- Sources in §10 reference the artefact built by `building-evidence-ledger`.
- For the lighter daily form, see `producing-daily-sitrep`.
