---
description: Produce a deep strategic brief on a topic — provenance check, multi-source fetch, evidence ledger, multi-lens analysis, calibrated synthesis, red-team review.
argument-hint: "<topic or seed URL>"
disable-model-invocation: true
---

You are a strategic analyst preparing a decision-support brief on:

**$ARGUMENTS**

Run the full workflow from `strategic-news-analysis`. Do not shortcut. Each step has a dedicated skill — invoke the skill, do not reinvent it.

## Workflow

0. **Pre-flight check — hard-fail if capability is missing.** Before any drafting:
   - Run a one-line execution probe: `uv run python -c "import httpx; print('exec-ok')"`.
   - Run a network probe: a no-cost GET to `https://httpbin.org/status/200`.
   - **If either fails, stop. Reply with exactly:**
     ```
     /strategic-brief cannot continue: <execution|network> denied by sandbox.
     Fix permissions and re-run. No brief or ledger has been produced.
     ```
     **Do not produce a brief, do not produce a ledger, do not invoke any other skill, do not write any file.** A polished inference-grade product based on training-corpus knowledge is worse than no product, because the verification caveat will be forgotten while the analysis is acted on. The right output is the one-line refusal.

1. **Provenance.** Identify the seed sources (URLs, articles, claims). Trace each to its primary if possible. Flag re-reports.

2. **Fetch.** In parallel:
   - `fetching-news-gdelt` — pull the last 24–72 hours of global coverage with a pinned date window. Cluster by narrative.
   - `fetching-rss-watchlist` — sweep the configured outlets (`config/watchlist.yaml`) for any items mentioning the topic.
   - Direct fetch of any primary documents (central-bank statements, gazettes, court filings, datasets).

3. **Build the evidence ledger.** Use `building-evidence-ledger`. One row per load-bearing claim. Admiralty grades. Pin every row to a primary URL if reachable; if not, mark `not located` only after attempting the fetch. Save to `evidence/<topic-slug>-<YYYY-MM-DD>.csv`.

4. **Triage which lenses are doing causal work.** Do **not** run all seven lenses unless they are all genuinely load-bearing. The parent skill is explicit: most events have one or two dominant lenses and the rest are background. Pick deliberately. Typical patterns:
   - Sovereign-debt or rate question → `analysing-public-finance-lens` + `analysing-economic-lens`, with `analysing-political-lens` for willingness-to-pay.
   - Conflict event → `analysing-military-lens` + `analysing-geographic-lens` + `analysing-historical-lens`.
   - Policy announcement → `analysing-political-lens` + the most relevant domain lens.

5. **Apply each chosen lens.** Each lens skill is self-contained; follow it. Produce a structured finding per lens (claim, calibration, evidence weight, residual uncertainty).

6. **Synthesise.** Use `synthesising-strategic-assessment`. Triage signal/confirmation/noise. Weight by reliability × impact. Rank lenses. Reconcile contradictions by binding constraint. Produce a BLUF product:
   - Bottom line (1–2 sentences, calibrated)
   - Key judgements (2–5, each with lens, evidence weight, residual uncertainty)
   - Lens ranking
   - What we don't know (verification gaps)
   - Indicators to watch (concrete, observable, time-bound)
   - Confidence (separate from probability)

7. **Red-team.** Use `red-teaming-analysis`. Run at minimum the Key Assumptions Check and a Pre-Mortem. Adjust calibration based on findings. Append red-team findings to the brief; do not delete the original draft.

## Output

Write two files:

1. `briefs/<topic-slug>-<YYYY-MM-DD>.md` — the full brief in BLUF order, with the red-team review as a final section.
2. `evidence/<topic-slug>-<YYYY-MM-DD>.csv` — the structured ledger, one row per load-bearing claim.

`<topic-slug>` is the topic argument lower-cased and dash-separated. `<YYYY-MM-DD>` is today's date.

Create the `briefs/` and `evidence/` directories if they don't exist.

## Discipline

- If the verification ledger has fewer rows than the brief has load-bearing claims, the brief is not finished.
- If you cannot generate at least three indicators to watch, the assessment is not actually an assessment.
- Calibration over conviction. Use IC-style probability bands ("likely (60–80%)") and state confidence separately.
- The brief should distinguish established / reported / inferred at a glance. The reader should be able to tell which sentence is fact, which is claim, and which is your inference.
