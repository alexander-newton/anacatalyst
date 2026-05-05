---
name: strategic-news-analysis
description: Use when interpreting a news story, policy announcement, conflict report, or data release where source provenance matters and headline framing may mislead. Triggers include "what does this mean", "is this important", "what happens next", "analyse this article", forecasting requests, and any multi-domain question.
---

# Strategic News Analysis

## Overview

A strategic analyst treats news as raw input, not finished knowledge. A report becomes intelligence only after its provenance has been assessed, its claims corroborated, and the event placed in structural context across multiple domains.

**Core principle:** *Verification before dissemination. Context before conclusion.*

If a plausible alternative interpretation cannot be sketched, the event has not been analysed — it has been copied. The job is not to summarise the article; it is to interrogate it.

## When to Use

Apply this skill when:
- A news item, social-media claim, or report is offered as evidence for a larger claim.
- The user asks "is this important", "what does this mean", "what happens next", "what's the significance".
- A headline framing might mislead (most "shock" headlines do).
- An event requires synthesis across domains (economy + politics + military, etc.).
- Forecasting or risk assessment is implicit in the request.
- There is a temptation to answer from a single article.

Do **not** use this skill for:
- Pure factual lookups ("when did X happen") — just look it up.
- Opinion or vibe requests where the user explicitly wants a take, not analysis.
- Topics where the user has already framed the analytical lens themselves and just wants execution.

## The Workflow

```
[1] Provenance → [2] Verify → [3] Contextualise → [4] Lens stack → [5] Hypotheses → [6] Synthesise → [7] Red-team
```

Skipping a step is the most common failure. The cost of step 1 is two minutes; the cost of skipping it is publishing nonsense. Steps 4, 6, and 7 each have dedicated sub-skills — this skill wires them together; the substantive work happens in those sub-skills.

**Sub-skill index:**

- *Lens stack (step 4):* `analysing-economic-lens`, `analysing-political-lens`, `analysing-historical-lens`, `analysing-demographic-lens`, `analysing-military-lens`, `analysing-public-finance-lens`, `analysing-geographic-lens`
- *Synthesis (step 6):* `synthesising-strategic-assessment`
- *Red-teaming (step 7):* `red-teaming-analysis`

### 1. Provenance — Who is telling you this?

Before reading the substance, establish the chain of custody:

- **Who is the publisher?** Wire (Reuters/AP/AFP/Bloomberg), national broadsheet, partisan outlet, state media, anonymous Telegram channel, individual on X?
- **Who is the original source?** A government press release? A named official? An anonymous "person familiar with the matter"? A think-tank report? An eyewitness? Another outlet (i.e., this is a re-report)?
- **What's the chain of custody?** Has this been quoted from another outlet, summarising a third? Each hop loses fidelity. Find the original document or statement.
- **Why is this published now?** Election cycle, policy fight, scheduled data release, leak with a target?

If "who originally said this, and where can I read the unedited statement" cannot be answered, what is on hand is a rumour, not a fact. Say so.

### 2. Verify — Two-source rule with diagnostic checks

Adapted from journalism's verification tradecraft and the Admiralty Code:

- **Two independent sources** for any consequential factual claim. Wire services count as one source; two outlets running the same wire is one source.
- **Don't trust experts about numbers** — go to the underlying data (the BLS release, the IMF table, the central bank statement, the company filing).
- **Read the actual statement, not the summary.** Officials are deliberate about wording; reporters paraphrase. The difference between "considering" and "decided" can be the entire story.
- **Images and video:** reverse image search (Google Images, TinEye, Yandex), check for geolocation cues (signage, vegetation, terrain, shadows for time-of-day), check publication history. Old footage resurfaces during conflicts. **AI-generated imagery is now cheap and common** — check for generative-model artefacts (mangled text, impossible reflections, anatomical inconsistencies, repeating-pattern backgrounds), and treat any image without a verifiable source chain as unconfirmed regardless of how plausible it looks.
- **"Officials say" / "sources tell us":** treat as B-grade until corroborated. One named source on the record outweighs five anonymous ones.

Use an **Admiralty-style rating internally**: source reliability A–F, information credibility 1–6. Most reporting is B2–C3. Be explicit about it in the output rather than laundering it into "experts say".

### 3. Contextualise — What is the structural backdrop?

A new event has meaning only against existing structure. Pull the relevant baselines:

- What was the trend before this? (5-year, 20-year if relevant.)
- What's normal for this country / sector / period? Establish the **base rate**.
- What precedent exists? What was tried last time?
- What had been forecast? Is this a surprise or expected?

A 2% inflation print is a non-event in 2019 and a relief in 2023. The number is the same; the meaning is opposite. **Always pull comparable historical data before concluding.**

### 4. Lens Stack — Multi-domain assessment

For any significant event, walk every relevant lens. Most events do not require all of them, but skipping the right one is the most common analytical error. The lenses interact; second-order effects usually live at the seam between two of them.

Each lens has a dedicated sub-skill containing the canonical frameworks, indicators, common mistakes, and a worked example for that domain. Use the lens sub-skill rather than working from the table alone — the table is an index, not the analysis.

| Lens | Core question | **Required sub-skill** |
|------|---------------|------------------------|
| **Economic** | Trade flows, prices, currency, supply chains, inflation, growth, terms of trade | `analysing-economic-lens` |
| **Political** | Governing coalition, opposition, public opinion, legitimacy, factional balance | `analysing-political-lens` |
| **Historical** | Precedent, cycles, path dependency, what was tried before and how it ended | `analysing-historical-lens` |
| **Demographic** | Population structure, migration, ethnic/sectarian composition, ageing, urbanisation | `analysing-demographic-lens` |
| **Military / Strategic** | Capabilities, deployments, alliances, deterrence balance, escalation ladder | `analysing-military-lens` |
| **Public Finance** | Debt sustainability, sovereign credit, fiscal space, currency mismatch | `analysing-public-finance-lens` |
| **Geographic** | Terrain, chokepoints, climate, resource endowments, infrastructure, distance | `analysing-geographic-lens` |

**Quick worked example — "Country X devalues currency 15%"** (illustrative only; for real analysis, run each relevant lens sub-skill):

- *Economic:* import inflation; export competitiveness up; dollar-priced commodities pricier locally. (Mundell-Fleming, pass-through.)
- *Political:* exporters and farmers gain; urban consumers lose; regime risk depends on which group is the base. (Selectorate, Stolper-Samuelson.)
- *Historical:* devaluation regimes that recur within a decade often face a confidence cliff. (Reinhart & Rogoff base rate.)
- *Demographic:* urban middle class is most exposed; protest capacity concentrates there.
- *Military:* foreign-currency procurement disrupted; spare-parts pipelines hit.
- *Public finance:* USD-denominated debt service balloons in local-currency terms; rating action probable. (Debt-accumulation identity, "original sin".)
- *Geographic:* port-adjacent provinces feel trade effects first; landlocked regions later.

The shape of the issue emerges only after walking the lenses. A single-lens read ("the economy will benefit from cheaper exports") is the kind of analysis that loses people money.

### 5. Hypotheses — Compete and falsify

Use **Analysis of Competing Hypotheses (ACH)** logic, even informally (Heuer 1999; Tradecraft Primer 2009):

1. Generate **3–5 plausible explanations** for the event before settling on one. Don't anchor on the first.
2. List the evidence — what's reported, what's known structurally, what's missing.
3. For each piece of evidence, ask: **which hypotheses does it discriminate between?** Evidence consistent with all hypotheses is non-diagnostic — set it aside.
4. **Try to falsify, not confirm.** The aim is to eliminate hypotheses, not to prop up the favourite.
5. State residual uncertainty explicitly. Use **calibrated probability language** ("highly likely (>90%)", "likely (60–80%)", "plausible", "cannot rule out", "very unlikely").

The point is not to feel certain. It is to know what is and is not known.

### 6. Synthesise — Rank, weight, calibrate

Lens analysis produces seven coherent reads. Synthesis is the discipline of *not pasting them together* — ranking lenses by which one is doing causal work, weighting findings by reliability and impact, calibrating probability and confidence separately, and producing a Bottom-Line-Up-Front (BLUF) product.

**REQUIRED SUB-SKILL:** `synthesising-strategic-assessment` — contains the full procedure for triage, weighting, lens ranking, reconciling contradictions, calibrated language, and BLUF formatting.

Quick reference of what the synthesised output should contain:

```
Bottom line: [1–2 sentences. The judgement, with calibrated probability and confidence.]
Key Judgements: [2–5, each tagged with lens, evidence weight, residual uncertainty.]
What's established / reported / inferred: [Distinguish source quality.]
Lens ranking: [Which lens is doing the causal work; which are background.]
Verification gaps: [What we don't know, listed explicitly.]
Indicators to watch: [Concrete, observable, time-bound.]
Confidence: [Separate from probability. Low / Moderate / High, with the reason.]
```

The reader should be able to tell at a glance which sentence is fact, which is claim, and which is the analyst's inference.

### 7. Red-team — Stress-test before finalising

A draft assessment is not a finished assessment. Before publishing, stress-test it: surface load-bearing assumptions, audit the evidence for weak sources, write out the strongest case against the conclusion, and imagine the assessment turned out wrong. Adjust calibration accordingly.

**REQUIRED SUB-SKILL:** `red-teaming-analysis` — contains the canonical structured analytic techniques (Key Assumptions Check, Quality of Information Check, Devil's Advocacy, Team A/Team B, Pre-Mortem, High-Impact/Low-Probability, Indicators of Change).

Red-teaming is **not optional for high-stakes assessments**. It is the step that catches confident conclusions resting on unexamined assumptions — the single most expensive analytical failure mode. If time is short, run at minimum the Key Assumptions Check (ten minutes) and the Pre-Mortem (ten minutes). Both are cheap, both routinely move the bottom-line band by 5–10pp and add useful indicators.

Update the synthesis (step 6) with the red-team's findings before finalising.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Reading the headline only | Find the original statement / data release / filing |
| Single-source acceptance | Apply two-source rule; flag if violated |
| "Officials say" treated as official position | Anonymous officials ≠ government policy |
| Mirror imaging (assuming the other side reasons like you) | Ask "what does this look like from their seat?" |
| Recency bias | Pull 5- and 20-year baselines before concluding |
| Confirmation bias | Generate alternative hypotheses **before** assembling evidence |
| Conspiracy reach | Coordination is hard; prefer parsimonious explanations |
| Galaxy-brain causal chains | Each conditional link is multiplicative; long chains have low overall probability |
| Ignoring base rates | "How often does this kind of thing actually happen?" |
| Single-domain analysis | Walk the lens stack; second-order effects live at the seams |
| Translation drift | Read the original-language statement when stakes are high |
| Skipping primary sources | Press releases, datasets, court filings, gazettes are usually one click away |

## Red Flags — Stop and Reassess

If two or more of these are present, the right output is "the reporting suggests X, but it's not yet established because Y" — not a confident conclusion:

- "Sources say" / "officials told [outlet]" with no further attribution.
- A claim that exactly matches one side's preferred framing.
- Numbers without a citation to the underlying release.
- Photos/video without time and place verification.
- A "leaked" document that conveniently surfaced just before a vote or decision.
- Translation of a foreign statement that subtly shifts the meaning (read the original).
- Strong claims based on absence of evidence ("there is no proof that…").
- A causal chain with five or more "would likely" links.
- A single outlet running a story that no one else has touched for 24+ hours.

## Tooling

This skill assumes a working Python environment (pandas, httpx/requests). The strategic analyst is *modern* — they pull data via API rather than copy-pasting from web pages where possible.

Key libraries by purpose:

- **News at scale:** `gdeltdoc` (GDELT 2.0 Doc API — global news, 100+ languages, tone scoring), `feedparser` (RSS for tracking specific outlets), `newsapi-python` (NewsAPI), `mediacloud` (Media Cloud).
- **Macro data:** `wbdata` (World Bank), `pandas_datareader` (FRED, OECD, Eurostat), IMF SDMX clients, `eurostat`.
- **Trade:** UN Comtrade API (`comtradeapicall`), WTO data portal, BACI (CEPII).
- **Conflict / events:** ACLED API, GDELT GKG events, UCDP.
- **Sanctions / regulation:** OFAC SDN list (XML/JSON feeds), EU consolidated list, UK OFSI list, OpenSanctions.
- **Energy:** EIA API (`eia-python`), IEA data.
- **Geospatial:** `geopandas`, `folium`, `shapely`, satellite via Sentinel Hub / Planet APIs.
- **NLP:** `spaCy` for named-entity extraction, `sentence-transformers` for narrative clustering across articles.
- **Fetching / parsing:** `httpx`, `selectolax` or `BeautifulSoup`, `trafilatura` for boilerplate removal.

For specific authoritative databases, APIs, and primary-source repositories organised by domain, see `data-sources.md`.

## Source Hierarchy

The general hierarchy of source reliability — top of list trumps bottom of list when they conflict:

1. **Primary documents** — the law, the contract, the dataset, the actual statement, the court filing.
2. **Official statistics** — national stats agencies, central banks, ministries, regulators.
3. **Multilateral institutions** — IMF, World Bank, OECD, UN agencies, BIS, IEA, SIPRI.
4. **Specialist trade press** — Janes, Lloyd's List, S&P Global Platts, Argus (paywalled, high quality).
5. **Wire services** — Reuters, AP, AFP, Bloomberg, Kyodo.
6. **Quality national press** — FT, NYT, WSJ, Le Monde, Nikkei, Economist (treat as journalism, not source).
7. **Think-tank analysis** — CSIS, IISS, Chatham House, RAND, Carnegie, ECFR (analysis, not fact; check funding).
8. **Specialist OSINT** — Bellingcat, ISW (verify methodology; usually transparent).
9. **General news / aggregators** — useful for spotting, never for sourcing.
10. **Anonymous social media** — leads only; never source.

State media (Xinhua, RT, IRNA, KCNA, etc.) is read as **a record of what that government wants known**, which is itself useful information — not as a source of independent fact.

## A Note on the Analyst's Discipline

The most expensive analytical failures come not from missing information, but from premature confidence. The discipline that separates analysts from commentators is the willingness to say "I don't know yet" while continuing to work the problem — and to update publicly when the picture changes. Calibration over conviction.
