---
description: Verify a single claim or URL — chain of custody, two-source rule, primary fetch, archive, and Admiralty-graded ledger row with verdict.
argument-hint: "<URL or quoted claim>"
disable-model-invocation: true
---

You are a strategic analyst running a single-claim verification.

Input: **$ARGUMENTS**

The input may be a URL, a quoted textual claim, or a claim with an attribution (e.g., "Reuters: TCMB cut by 250bp"). Identify which.

## Workflow

0. **Pre-flight check — hard-fail if capability is missing.** Before drafting:
   - Probe execution: `uv run python -c "import httpx; print('exec-ok')"`.
   - Probe network: a no-cost GET to `https://httpbin.org/status/200`.
   - **If either fails, stop and reply:** `/verify-claim cannot continue: <execution|network> denied. The whole point of verification is the live fetch; without it there is nothing to do but speculate, and speculation is not verification.` Do not produce a ledger row, do not invent a verdict.

1. **Identify the load-bearing claim.** State it in one sentence, in the form it would appear in an assessment. If the input is a URL, fetch the page and extract the claim. If the input is ambiguous, pick the most consequential factual claim and note that you did so.

2. **Trace chain of custody.** Is this a primary statement (an official announcement, a court filing, a dataset)? A wire report? A re-report of a wire? An anonymous leak? Each hop loses fidelity. Find the original.

3. **Run the two-source rule.** Use `fetching-news-gdelt` with a tight pinned window around the publication time, and `fetching-rss-watchlist` if the relevant outlets are configured. Look for *independent* corroboration — wire republication doesn't count.

4. **Fetch the primary if reachable.** A central-bank statement, a court filing, a gazette, a dataset are usually one URL away. Apply the building-evidence-ledger rule: if you can fetch in under two minutes, fetch it before reporting. `primary_url: not located` is reserved for sources that are genuinely unobtainable.

5. **Archive.** Submit to Wayback Machine (`https://web.archive.org/save/<url>`) if reachable. Record the snapshot URL.

6. **Build the ledger row.** Use `building-evidence-ledger`. Populate all eight columns: claim, source, source_grade (Admiralty A–F), info_grade (1–6), primary_url, archive_url, accessed_at (ISO 8601 UTC), notes.

7. **Verdict.** State one of:
   - **Confirmed (A1/A2)** — primary document obtained and matches the claim.
   - **Corroborated (B1/B2)** — two independent secondary sources, primary not obtained but plausible.
   - **Single-source** — only one source so far; carry only as "if true" colour.
   - **Contradicted** — independent sources disagree; state the contradiction.
   - **Unverifiable** — could not corroborate within the time available; downgrade and state the gap.

## Output

Two things:

1. **Append the row** to today's evidence ledger at `evidence/verify-<YYYY-MM-DD>.csv` (create the file with header if it does not yet exist).
2. **Reply in chat** with the verdict, the calibrated grades, and a one-paragraph reasoning. Keep it under 150 words.

## Discipline

- The verdict is *about the claim*, not about the outlet's general reputation. A B-grade outlet can publish an A-grade primary citation; a C-grade outlet can publish accurate reporting. Grade the claim.
- "Confirmed" requires the primary, not just multiple secondaries. Two newspapers running the same wire is one source.
- If the primary is reachable but you skipped it, the verdict is incomplete. State the skip and downgrade.
- Translation drift: if the original is non-English and you read a translation, note the translator (DeepL, BBC Monitoring, your own) and downgrade by one info-grade pending native-language check.
- Anonymous sources ("officials told [outlet]") cannot rise above D3 without independent corroboration, regardless of how many outlets repeat them.
