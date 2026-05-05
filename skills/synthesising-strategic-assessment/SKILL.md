---
name: synthesising-strategic-assessment
description: Use when lens analysis is complete and outputs must be combined into a single prioritised, calibrated product for a decision-maker. Triggers include "give me the bottom line", "what matters most", "executive summary", "what's the call", or any briefing memo, BLUF, or decision-support output.
---

# Synthesising a Strategic Assessment

## Overview

Lens-by-lens analysis produces seven coherent reads of an event. Synthesis is the discipline of *not pasting them together*. A real assessment ranks the lenses by which one is doing causal work in this case, weights claims by source reliability and structural impact, foregrounds what is actually decision-relevant, and is honest about residual uncertainty.

**Core principle:** *A good assessment can be wrong but cannot be vague.* The reader must be able to extract the bottom line, the reasoning, the evidence, and what would change the assessment — in that order, in that priority.

## When to Use

- After running the lens stack from the parent `strategic-news-analysis` skill on a non-trivial event.
- Producing an executive summary, briefing memo, or "bottom line up front" for a decision-maker.
- Reconciling findings across lenses that point in different directions.
- Deciding what to lead with and what to relegate.
- Any time multiple streams of analysis need to be combined into a single product.

## The Workflow

```
[1] Triage  →  [2] Weight  →  [3] Rank lenses  →  [4] Reconcile  →  [5] Calibrate  →  [6] Format
```

### 1. Triage — Signal vs noise

For each finding from the lens stack, classify it:

- **Signal** — changes a previously-held estimate of probability or magnitude.
- **Confirmation** — consistent with prior view, doesn't update.
- **Noise** — does not bear on the assessment regardless of direction.

Most news, even when the lenses produce comments on it, is *noise* relative to the strategic question. The first synthesis move is to discard the noise without ceremony. If a lens produced only noise, say so and move on.

A useful test: *if this finding turned out to be wrong, would my overall assessment change?* If no, it's not load-bearing. Don't lead with it.

### 2. Weight — Reliability × Impact

Every finding has two dimensions worth scoring (informally is fine):

- **Reliability** — what's the source quality? (Admiralty A1 vs C3 vs E5; primary document vs single-source claim vs inference.)
- **Impact** — if true, how much does this matter for the assessment?

Plot findings on a 2x2 (high/low on each axis):

|              | **High impact** | **Low impact** |
|--------------|-----------------|----------------|
| **High reliability** | **Lead with this.** Anchor of the assessment. | Background; mention briefly. |
| **Low reliability** | **Flag prominently.** "If true, …" — name the consequence and the verification gap. | Cut. Don't pad with low-quality, low-impact items. |

The "if true" quadrant is dangerous and important. Low-reliability + high-impact items must be carried with explicit caveats — readers extract the consequence and forget the caveat unless it's structural.

### 3. Rank lenses — Which one is doing the causal work?

Not all seven lenses matter equally for every event. One or two usually dominate; the rest are background. Identify which.

Diagnostic questions:
- *Removing this lens, does the assessment change?* Lenses that pass this test are the dominant ones.
- *What would the analyst with no access to this lens miss?* The biggest answer points to the dominant lens.
- *Where do the lenses contradict?* The contradiction is itself the story; foreground it rather than averaging it out.

Rank, don't list. A synthesis that says "economic, political, military, demographic factors all matter" has done no work. A synthesis that says "this is fundamentally a fiscal-credibility question with secondary political consequences" has.

### 4. Reconcile — When lenses disagree

Two lenses pointing in opposite directions is normal and informative. Don't average. Instead:

- **Trace the disagreement.** Is one lens speaking to short-term, the other long-term? One to capability, the other to intent? Different time horizons or different actors usually explain apparent contradictions.
- **Identify the binding constraint.** When a politician *wants* policy A but fiscal space rules it out, the public-finance lens dominates over the political. Find which lens supplies the constraint others must respect.
- **Surface the disagreement to the reader.** "Politically the move is desirable for X; fiscally it is unaffordable without Y; the binding constraint is fiscal." This is more useful than a smoothed compromise.

### 5. Calibrate — Probability and confidence language

Use the Intelligence Community–style calibrated probability scale:

- **Almost no chance** (<5%) / **Very unlikely** (5–20%) / **Unlikely** (20–45%)
- **Roughly even chance** (45–55%)
- **Likely** (55–80%) / **Very likely** (80–95%) / **Almost certainly** (>95%)

Distinguish probability from confidence:

- **Probability** — how likely is it?
- **Confidence (in the assessment itself)** — *low / moderate / high*, based on quality and quantity of evidence and degree of analytical disagreement.

A "likely (65%)" judgement with *low confidence* is a different statement from "likely (65%)" with *high confidence*. The first invites monitoring; the second invites planning.

Never use "could", "may", "might" without quantification — they smuggle wide ranges past the reader.

### 6. Format — BLUF and Key Judgments

Use the **Bottom Line Up Front (BLUF)** structure favoured by national-intelligence products. The reader's first sentence should be the conclusion; everything after is justification and qualification.

Standard structure:

```
1. Bottom line / Key Judgement
   One paragraph. The conclusion. Calibrated.

2. Key Judgments (2–5)
   Each: a claim with calibrated language, the lens it lives in,
   the evidence weight, and the residual uncertainty.

3. Reasoning
   The lens-by-lens reasoning, ranked.

4. What we don't know / verification gaps
   Explicit, not buried. The honest version of what's still open.

5. Indicators to watch
   Concrete, observable, time-bound. What would change the call.

6. Sources
   The provenance trail. Distinguish primary from secondary, cite specifics.
```

The "indicators to watch" section is the single most undervalued part. It converts an assessment into a *living* product — readers know what to monitor and what should make them call the analyst again.

## Quick Reference

| Element | Done well | Done badly |
|---------|-----------|------------|
| Bottom line | One paragraph, calibrated, falsifiable | "It's complicated"; "various factors" |
| Lens ranking | One or two dominate, rest are explicit context | All seven listed equally; reads like a checklist |
| Lens disagreement | Surfaced, traced, binding constraint named | Smoothed into bland consensus |
| Probability | Numerical band + word ("likely (60–70%)") | "Could", "may", "potentially" without bounds |
| Confidence | Stated separately from probability | Conflated with probability |
| Verification gaps | Listed explicitly | Buried in mid-paragraph hedges |
| Indicators | Concrete, observable, time-bound | Generic ("watch the situation") |
| Provenance | Specific cites, primary vs secondary distinguished | "According to reports" |

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Listing lens outputs without ranking | Rank by causal weight; foreground the dominant lens |
| Averaging contradictory lenses | Trace the contradiction; identify the binding constraint |
| Burying the bottom line | BLUF: conclusion first, evidence after |
| Smuggling uncertainty in vague verbs | Use calibrated probability language with bands |
| Conflating probability with confidence | Two different things; report both separately |
| Padding with low-impact findings | Use the 2×2; cut the low-impact-low-reliability quadrant |
| "Could go either way" without indicators | If the assessment can't generate indicators, it's not actually an assessment |
| Treating reliability as binary | Rate it; flag low-reliability claims that are load-bearing |
| Recapitulating instead of judging | The reader has the article; they want your call, not a summary |
| Anchoring to first lens | Generate hypotheses *before* deep-diving any single lens; come back at the end |

## Worked Example

Suppose lens analysis on a sovereign-debt downgrade has produced the following raw outputs:

- *Economic:* Growth slowing; current-account deficit widening; FX under pressure. (medium reliability — recent data only)
- *Political:* Government coalition holds 51% majority; finance minister credibility moderate; opposition gaining in polls. (high reliability — primary)
- *Historical:* Country has experienced two debt crises in the last 30 years, both following similar fiscal trajectories. (high reliability)
- *Demographic:* Long-run constraint, ageing population, but not material at this time horizon. (high reliability, low impact)
- *Military:* Not directly relevant. (n/a)
- *Public finance:* Debt/GDP at 95%, projected to rise; r > g; debt-stabilising primary balance not achievable under current policy; reserves cover 3 months of imports; ~40% of debt in foreign currency. (high reliability — IMF Article IV + market data)
- *Geographic:* Energy-importing economy exposed to global oil prices via FX channel. (medium reliability — implied chain)

**Synthesis:**

1. **Triage:** Demographics is noise at this horizon. Geography is background (a transmission channel, not a driver). Military lens drops.
2. **Weight:** Public-finance findings are high-reliability/high-impact. Political findings are high/medium-impact. Historical is high/medium-impact (informs the base rate). Economic findings are medium-reliability (volatile data, recent only).
3. **Rank lenses:** **Public finance is dominant.** This is fundamentally a debt-sustainability question with a political-feasibility constraint. Political lens is secondary — it supplies the *willingness-to-pay* judgement layered onto the *capacity* question. Historical lens supplies the base rate.
4. **Reconcile:** No deep contradiction. Public finance and historical agree the trajectory is bad. Political lens supplies the *binding constraint*: even if the technocratic adjustment is identifiable, can the government deliver it? Coalition arithmetic suggests not.
5. **Calibrate:** "*Default or restructuring within 18 months is **likely (60–75%)**, with **moderate confidence**.* Confidence is moderate — not high — because debt crises can be averted by exogenous events (external bailout, commodity-price recovery, election surprise) that history shows are not rare."
6. **Format:**

```
BOTTOM LINE: Default or restructuring within 18 months is likely (60–75%) with
moderate confidence. The binding constraint is political: a debt-stabilising
primary surplus is technically identifiable but politically not deliverable
under the current coalition.

KEY JUDGEMENTS:
- Public-finance arithmetic does not stabilise: r > g, primary balance well
  short of debt-stabilising level, FX-debt share amplifies any depreciation
  shock. (High reliability — IMF DSA, market data.)
- Coalition cannot deliver fiscal adjustment of the required size. Base case
  is partial measures, missed targets, IMF programme negotiation by Q3.
  (High reliability on coalition arithmetic; medium on programme timing.)
- Historical base rate: two prior crises with similar trajectory both ended
  in restructuring within 18–24 months. (High reliability.)

WHAT WE DON'T KNOW:
- Whether external bilateral support (named partners) materialises.
- Whether opposition would tactically support an IMF deal or block it.
- Trajectory of global commodity prices over next 6 months.

INDICATORS TO WATCH:
- Next two sovereign auctions: bid-to-cover and tail.
- 5-year CDS spread crossing 800bp.
- Reserves below 2 months of imports.
- IMF mission announcement.
- Coalition partner public statements diverging from PM.
- Commodity price moves > 15% in either direction.
```

## Canonical References

- US Office of the Director of National Intelligence, *Intelligence Community Directive 203* (analytic standards)
- *Intelligence Community Directive 206* (sourcing requirements)
- Tetlock, *Superforecasting* (calibration discipline)
- Heuer & Pherson, *Structured Analytic Techniques for Intelligence Analysis*
- US Government, *A Tradecraft Primer*

## Cross-References

- Run lens analysis first using the seven lens skills (`analysing-economic-lens`, `analysing-political-lens`, `analysing-historical-lens`, `analysing-demographic-lens`, `analysing-military-lens`, `analysing-public-finance-lens`, `analysing-geographic-lens`).
- After synthesis, **run `red-teaming-analysis` against the bottom-line judgement** before finalising. Synthesis without red-teaming is half-finished work.
