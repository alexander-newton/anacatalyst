---
name: red-teaming-analysis
description: Use after a strategic assessment has been drafted and before it is finalised, especially before high-stakes decisions or when the analysis feels too clean. Triggers include "challenge this", "what could be wrong", "stress-test", "devil's advocate", "what would change my mind", or "what's the contrarian view".
---

# Red-Teaming Analysis

## Overview

Red-teaming is the disciplined attempt to break your own assessment before reality does. It is not contrarianism for its own sake — it is the systematic application of structured analytic techniques designed by the intelligence community to surface assumptions, alternative hypotheses, and overlooked scenarios.

**Core principle:** *Your assessment must survive a hostile reading by someone with the same evidence and a different prior. If you cannot defend it against your own best attack, the conclusion is not yet ready.*

The most expensive analytical failures are not from missing evidence — they are from confident conclusions resting on assumptions nobody examined.

## When to Use

- **Always before finalising a high-stakes assessment.** This is the default; it is not optional.
- The team converged quickly, with little disagreement.
- The bottom line aligns suspiciously well with the analyst's priors or the customer's preferences.
- A senior reviewer or decision-maker is about to act on the product.
- The assessment claims certainty above 80% on a contested question.
- Stakes are asymmetric — a wrong call would be much costlier than a marginally over-cautious one.

Skip only when stakes are genuinely low and time pressure is acute (still: do at least the Key Assumptions Check; it takes ten minutes).

## The Techniques

These are drawn from the intelligence-community canon (Heuer & Pherson; CIA *Tradecraft Primer*; ODNI tradecraft standards). Each technique addresses a specific failure mode.

### 1. Key Assumptions Check (KAC)

**Purpose:** Surface the assumptions the analysis is resting on, then test each.

**Procedure:**
1. List all assumptions — both stated and unstated. Be exhaustive; include things that "go without saying."
2. For each, ask:
   - Is this assumption still valid? Has the world changed?
   - What would happen if this assumption were wrong?
   - How would I know if it were wrong?
3. Categorise each assumption as: **solid, supported, caveated,** or **unsupported.**
4. Any unsupported or caveated assumption that the conclusion *depends on* must be flagged in the final product.

A useful starter list of assumptions to test even when not stated:
- "Actor X is rational in the way I'm modelling rationality."
- "Recent trends will continue."
- "The political coalition will hold."
- "No major exogenous shock in the time horizon."
- "Translations and reports accurately capture what was said."
- "The data series I'm using is comparable across the period."

**Output:** A short list of load-bearing assumptions, each with status. Anything weaker than "supported" enters the assessment's caveats and indicators.

### 2. Quality of Information Check

**Purpose:** Audit the evidence base; find where the analysis leans on weak sources.

**Procedure:**
1. List the key facts the assessment depends on.
2. For each, identify the ultimate source (not the citation chain — the original).
3. Rate reliability (Admiralty A–F) and credibility (1–6).
4. Flag any claim where the conclusion would change if that single source were wrong.
5. Look specifically for: single-sourced claims, anonymous sources, translated material, satellite-derived inferences, social-media-only events, paywalled secondary sources you haven't actually read.

**Output:** A revised evidence inventory with quality ratings. Rewrite the load-bearing claims that depend on weak sources to acknowledge the dependency.

### 3. Devil's Advocacy

**Purpose:** Have someone (or yourself, in an explicit role) construct the strongest case against the conclusion.

**Procedure:**
1. State the assessment's conclusion clearly.
2. Adopt the role: *I will argue the opposite is true.* Use only evidence already in hand or that could plausibly exist.
3. Find: alternative explanations for the same evidence; evidence the assessment minimised; assumptions that would change the conclusion if reversed.
4. Force yourself to write the alternative case as if it were the real assessment. Do not strawman.
5. Compare: what is the marginal evidence that distinguishes the original conclusion from the devil's advocate's? Is it as strong as you thought?

**Output:** A short statement of the strongest counter-case, the evidence that would shift the assessment toward it, and an honest reassessment of the original conclusion's confidence level.

### 4. Team A / Team B

**Purpose:** Where multiple plausible interpretations exist, force structured competition between them rather than premature consensus.

**Procedure:**
1. Identify two (occasionally three) substantively different interpretations of the same evidence.
2. Build out each as a complete case — its own logic, its own use of the evidence, its own indicators.
3. Compare on:
   - Which evidence is *diagnostic* between them? (Evidence consistent with both is non-discriminating.)
   - Which assumptions are different?
   - What would each predict next? (The predictions become indicators.)
4. Do not settle on the "winner" prematurely; carry both forward as live hypotheses with assigned probabilities and watch the indicators.

**Output:** Two structured cases, the diagnostic evidence between them, and indicators that would resolve in favour of one or the other.

### 5. Pre-Mortem

**Purpose:** Defeat hindsight bias *before* the event by imagining the assessment turned out wrong.

**Procedure:**
1. State the assessment.
2. Imagine: *It is six months from now. The assessment was clearly wrong. The decision based on it failed badly.*
3. Ask: *What is the most plausible story for how this happened?* Generate 3–5 such stories.
4. Trace each backward: what indicator, knowable today or in the next few weeks, would have warned us?
5. Add those indicators to the watch list. Reconsider the probability if any are particularly compelling.

**Output:** Failure scenarios with leading indicators. Often produces the most useful additions to the "indicators to watch" list.

### 6. High-Impact / Low-Probability Analysis

**Purpose:** Avoid systematic underweighting of low-probability events that would matter enormously.

**Procedure:**
1. List events that are individually unlikely but would have outsized effects on the assessment if they occurred.
2. For each, write what the world would look like immediately afterward.
3. Identify the chain of causation — is the event truly low-probability, or is it just unfamiliar?
4. Add to the assessment a brief explicit treatment of these tail risks, with rough probability bands.

This technique catches "we didn't see it coming" failures. The events were thinkable; nobody thought them.

### 7. What If? Analysis

**Purpose:** Explore implications by assuming a specified low-probability event has occurred and working forward.

**Procedure:**
1. Specify the event ("Country X's leader dies suddenly", "a major bank fails", "the canal closes for 6 months").
2. Working forward from the moment of occurrence, trace consequences across all seven lenses.
3. Identify what would be done in the first week, first month, first quarter — by which actors.
4. Compare to the baseline assessment: which conclusions hold under the alternative scenario, which break?

**Output:** A scenario sketch, often useful as an annex to the main assessment.

### 8. Indicators / Signposts of Change

**Purpose:** Convert the assessment into a *living* product with explicit triggers.

**Procedure:**
1. For each key judgement, ask: *What would I expect to see if this were true? What if it were false?*
2. Generate concrete, observable, time-bound indicators.
3. Specify thresholds where possible. ("CDS spread crossing 600bp" is better than "rising spreads".)
4. Distinguish leading indicators (warn of change) from confirming indicators (validate it).
5. Assign someone (yourself, named feeds, a script) to monitor each.

**Output:** A monitoring matrix that hands the assessment forward in time.

## Quick Reference

| Failure mode | Right technique |
|--------------|-----------------|
| Premature consensus | Devil's Advocacy, Team A/Team B |
| Unstated assumptions driving conclusion | Key Assumptions Check |
| Weak evidence treated as strong | Quality of Information Check |
| Hindsight bias / overconfidence | Pre-Mortem |
| Tail-risk underweighting | High-Impact/Low-Probability |
| Static analysis | Indicators of Change |
| Unfamiliar adversary's perspective | Red Hat / Role-Playing (model the adversary's logic) |
| One scenario assumed | What If? / Alternative Futures |

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Skipping red-team because "we already considered alternatives" | Considering ≠ structured technique; do the procedure |
| Doing red-team and ignoring the findings | If you red-team and don't update, you've performed theatre |
| Self-red-teaming without role discipline | Force the alternative case fully; do not strawman |
| Only attacking the conclusion, not the assumptions | KAC first; the assumptions are usually where the failure lives |
| Treating contrarianism as red-teaming | Random disagreement is noise; structured techniques produce signal |
| Writing red-team as appendix to ignore | Findings must update the bottom line, the confidence level, or the indicators |
| Red-teaming late | Do it *before* finalising; once a draft is socialised, reversing is much harder |
| Confusing "we couldn't find a flaw" with "no flaw exists" | Failure to falsify ≠ proof |

## Worked Example

Consider the synthesis from `synthesising-strategic-assessment` — the sovereign-debt assessment concluding default or restructuring within 18 months is "likely (60–75%) with moderate confidence."

**Key Assumptions Check:**
- *Assumption: r > g over the projection.* Tested — yes, supported by current and forward-looking rates and growth projections, but sensitive to global rate moves. **Caveated.**
- *Assumption: coalition will not deliver adjustment.* Based on current coalition arithmetic. **Supported but contingent** — a junior partner shift could change this.
- *Assumption: no exogenous bailout.* **Unsupported** — bilateral support from a named partner is mentioned in the news cycle. Could change the picture.
- *Assumption: historical base rate (2 of 2 crises ended in restructuring) is informative.* **Supported but n=2** — small sample.

**Quality of Information Check:** Public-finance data is high-quality (IMF, primary). Political assessment relies partly on polling and political reporting (B2). The "exogenous bailout unlikely" view rests on absence of public commitments, not positive evidence. Flag.

**Devil's Advocacy:** *The case for no default within 18 months.* Bilateral partner provides lifeline; IMF programme produces enough adjustment to extend; commodity prices recover. Probability: not 25–40% but plausibly higher given the partner's strategic interest in the regime. The original assessment may be underweighting the bailout pathway.

**Pre-Mortem:** *18 months from now, no default occurred.* Most plausible stories: (1) bilateral lifeline materialised; (2) IMF programme bridged with creditor forbearance; (3) commodity windfall closed the gap; (4) restructuring occurred but technically wasn't classified as default. Indicators added: bilateral diplomatic activity, IMF mission timing, commodity prices, debt-exchange announcements distinct from defaults.

**Result:** Move from "likely (60–75%)" to "**likely (55–70%)**" — a small but real downward adjustment reflecting the bailout pathway. Add the bilateral-partner indicator prominently. Flag the exogenous-bailout assumption explicitly in the assessment. Confidence remains moderate.

The point is not a dramatic reversal — it is calibration. Red-teaming this assessment moved the probability band by about 5pp and added two important indicators. That is what success looks like.

## Cross-References

- `synthesising-strategic-assessment` — produces the assessment that gets red-teamed.
- `analysing-historical-lens` — its analogy-handling discipline (likeness/difference/presumption) is itself a red-team technique applied to specific historical claims.
- The parent `strategic-news-analysis` — its Common Mistakes table maps to many of the failure modes red-teaming addresses; that table is what red-teaming operationalises.

## Canonical References

- Heuer & Pherson, *Structured Analytic Techniques for Intelligence Analysis*
- US Government, *A Tradecraft Primer: Structured Analytic Techniques for Improving Intelligence Analysis* (2009)
- Heuer, *Psychology of Intelligence Analysis* (1999)
- Klein, "Performing a Project Premortem" (HBR, 2007)
- Tetlock & Gardner, *Superforecasting*
- ODNI, *Intelligence Community Directive 203* (analytic standards)
