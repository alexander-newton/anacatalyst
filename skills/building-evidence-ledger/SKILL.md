---
name: building-evidence-ledger
description: Use when verification of multiple claims is required, before drafting any strategic assessment that will name a number, attribute a position, or assert a fact. Triggers include "is this real", "what's the source", "verify this", "two-source rule", any analysis with consequential factual claims, and any moment when a draft is about to cite a figure or statement without a primary citation.
---

# Building an Evidence Ledger

## Overview

A strategic assessment is only as good as the chain of custody behind every load-bearing claim. The evidence ledger is **the artefact that makes verification real**: a structured table of every claim the assessment depends on, with its source, source grade, primary URL, archive URL, and accessed timestamp.

**Core principle:** *No claim makes it into the assessment without a row in the ledger.* If you cannot produce the ledger, you have not verified — you have summarised.

The ledger is not paperwork. It is the difference between an analyst and a commentator.

## When to Use

- **Always**, before drafting a strategic assessment that names a number, attributes a position to a named actor, or asserts a contested fact.
- When applying the verification step of `strategic-news-analysis` (step 2).
- When a single article is being used to anchor a larger conclusion — the ledger forces the second-source check.
- Before submitting any briefing product to a decision-maker.
- When the user asks "is this real" / "what's the source" / "can we verify".

**Skip only when:**
- The deliverable is an explicit opinion piece, not analysis.
- The user has explicitly waived sourcing ("just give me your read").
- Stakes are genuinely trivial *and* the analyst is prepared to say so out loud.

The temptation to skip is strongest under time pressure, when the claim "feels true", or when the analyst is already 80% drafted. **All three are signals to build the ledger anyway.** If the deadline is too short to verify, the honest output is "this is unverified, here is what I can say with that caveat" — not a confident conclusion with hidden gaps.

## The Ledger Format

Every load-bearing claim gets one row. Use CSV (`evidence/<topic>-<YYYY-MM-DD>.csv`) or a markdown table inline if the assessment is short. Required columns:

| Column | Content | Notes |
|---|---|---|
| `claim` | The factual claim, in one sentence, in the form it will appear in the assessment | If you can't state the claim crisply, you don't yet know what you're verifying |
| `source` | Publisher and outlet (e.g. "Reuters wire", "MOFCOM communique 2024-08-12", "@named_account on X") | The named outlet, not "media reports" |
| `source_grade` | Admiralty source reliability: **A** (reliable), **B** (usually reliable), **C** (fairly reliable), **D** (not usually reliable), **E** (unreliable), **F** (cannot judge) | Wire services + named officials = B; primary documents = A; anonymous = D unless corroborated |
| `info_grade` | Admiralty information credibility: **1** (confirmed by independent sources), **2** (probably true), **3** (possibly true), **4** (doubtful), **5** (improbable), **6** (cannot judge) | Two independent sources = 1; single high-quality source = 2 |
| `primary_url` | Link to the **original** statement / dataset / filing | Not a re-report. If the original is not findable, mark "not located" and downgrade |
| `archive_url` | Wayback Machine snapshot URL or other archive | Pages disappear; archive at the moment of citation |
| `accessed_at` | ISO 8601 timestamp when you read it | Lets you reconstruct what was visible when |
| `notes` | Caveats, translation issues, contradictions with other sources | Where dissent and uncertainty live |

A worked CSV template is in `ledger_template.csv` in this folder.

## The Iron Rules

1. **One row per load-bearing claim, before drafting.** If a sentence in the draft refers to a fact, the fact has a row. Backfill is cheating — by the time you backfill, you have already anchored to it.
2. **No claim above grade D5 enters the assessment without a flag.** Low-reliability claims may be carried, but they must be marked "if true, …" in the prose, not laundered into "experts say".
3. **The two-source rule is enforced through the ledger.** A consequential factual claim with one row gets a flag. If you cannot find a second independent source, the assessment says so.
4. **Wire services count as one source.** Two outlets running the same Reuters wire is one row, not two. The ledger should make this visible.
5. **Anonymous sources are D-grade until corroborated.** "Sources told [outlet]" is one row, grade D, info-grade 3 at best.
6. **Translations are recorded.** If the primary source is non-English, the row notes that, and ideally cites both the original-language URL and the translation used.
7. **If the primary source is one URL away, fetch it before drafting.** "Marked as gap" is not the same as "verified". `primary_url: not located` is reserved for sources you genuinely cannot obtain — paywalled with no access, foreign-language gazette not yet posted, internal document — *not* for the central bank's website you simply did not open. The two-minute fetch beats the twenty-minute caveat.
8. **The ledger is a file, not a paragraph.** A markdown table inside the prose is *better than nothing* but is not a ledger. The ledger lives at `evidence/<topic>-<YYYY-MM-DD>.csv` (or .md) and survives the meeting. If your director walks out with the one-pager and you cannot hand them the ledger separately, you do not have one.

## Worked Example

Topic: "Is the Turkish central bank rate cut real and what was the size?"

Draft assessment (1 hour before deadline) cites: a 250bp cut.

Ledger built before drafting:

| claim | source | source_grade | info_grade | primary_url | archive_url | accessed_at | notes |
|---|---|---|---|---|---|---|---|
| TCMB cut 1-week repo from 35.0% to 32.5% on 2024-XX-XX | TCMB press release | A | 1 | tcmb.gov.tr/wps/...press-release | web.archive.org/...press-release | 2024-XX-XX 08:14Z | **Primary document.** Confirms 250bp, not 350bp. |
| Markets had expected a hold | Reuters wire | B | 2 | reuters.com/...turkey-rate-cut | web.archive.org/... | 2024-XX-XX 08:15Z | Single wire. Acceptable for "expectations" colour, not a load-bearing claim. |
| Cut was driven by political pressure ahead of municipal elections | sell-side analyst note (Bank X) | C | 3 | (note distributed by email; no public URL) | n/a | 2024-XX-XX 08:18Z | **Anonymous sources within the note.** Treat as one analyst's read, not fact. Do not present as established. |
| Actual cut was 350bp, communique to be amended | EM commentator on X (@handle) | D | 4 | x.com/handle/status/... | web.archive.org/... | 2024-XX-XX 08:20Z | Single anonymous claim, contradicts primary document. **Discard.** |

The ledger collapses the question. Row 1 (primary, A1) settles size at 250bp. Row 4 (D4, contradicted by row 1) is dismissed. Row 3 is carried as "if true" colour, not as a finding. The one-pager writes itself, calibrated, with the verification visible.

Without the ledger, the analyst is choosing between three confident-sounding sources by gut feel.

## Quick Reference

| Situation | Ledger move |
|---|---|
| Claim is in your draft but no ledger row | **Stop drafting.** Add the row or remove the claim. |
| Wire service is your only source | Flag in the draft: "single-source wire". Look for a primary document. |
| "Sources familiar with the matter" | Grade D until corroborated. State that. |
| Two outlets, one wire | One row, not two. Fix the ledger. |
| Image or video evidence | Reverse-image-search; record TinEye/Yandex hit count and earliest known date in `notes`. |
| Foreign-language statement | Cite original-language URL + translation. Note translator (DeepL, BBC Monitoring, your own). |
| Number from a database | Cite the table, not the article that summarised it. |
| Primary source is one URL away (central-bank site, court filing, gazette, dataset) | **Fetch it before drafting.** Two-minute task. "Marked as gap" is not verification. |
| You genuinely can't find the primary (paywalled, foreign gazette not posted, internal document) | Mark `primary_url: not located`. Downgrade the row. State the gap explicitly in the assessment's "what we don't know". |
| Time pressure tempts you to skip the ledger | Build a 4-row ledger covering only the load-bearing claims. Less is fine. Zero is not. The ledger takes longer to argue about than to write. |
| You wrote the ledger as a markdown table inside the prose | Move it to `evidence/<topic>-<date>.csv`. It must be a separate artefact, not embedded in the brief. |

## Common Mistakes

| Mistake | Fix |
|---|---|
| Treating the ledger as documentation produced *after* the assessment | Build it *before* drafting. By the time you backfill, you have already anchored to claims. |
| Grading every wire as A1 | Wires are usually B2. Reserve A1 for primary documents and direct datasets. |
| Counting two outlets running the same wire as two sources | One wire, one row. Aggregator chains do not multiply independence. |
| Allowing "experts say" or "according to reports" into the prose | Trace every "say" to a named source, or flag as unverifiable. |
| Not archiving | Pages move, get edited, disappear. Wayback or screenshot at the moment of access. |
| Ledger lives in your head | If it is not a file (or at least a markdown table in the draft), it is not a ledger. |
| Skipping the ledger because "the claim is obvious" | The ones that "feel obvious" are exactly the ones you fail to verify. |
| Padding with low-relevance rows | Load-bearing claims only. Decorative rows obscure the diagnostic ones. |

## Red Flags — Stop and Build the Ledger

If two or more of these are present, stop drafting:

- The draft cites a number with no row showing where it came from.
- The draft attributes a position to a named actor without quoting an actual statement.
- "Reports indicate" / "according to multiple outlets" with no specifics in the ledger.
- The draft is taking a side between contradictory sources without grading either.
- You can't immediately produce the primary URL for the most consequential claim in the assessment.
- A claim originally from social media is now in the draft without an A or B-grade corroboration.
- You are about to file the assessment in less than 10 minutes and do not have a ledger file.
- You wrote `primary_url: not located` for a source whose website you did not actually open.
- The ledger only exists as a table inside the prose, not as a separate file the principal could be handed.

## Cross-References

- This skill operationalises step 2 (Verify) of `strategic-news-analysis`.
- Run `archiving-with-wayback` (when written) to populate `archive_url` cells.
- The synthesis stage uses the ledger directly: `synthesising-strategic-assessment`'s reliability×impact 2×2 reads off the `source_grade` × `info_grade` columns.
- Red-teaming requires the ledger as an input: `red-teaming-analysis`'s Quality of Information Check is impossible without it.

## A Note on Discipline

The expensive failure is not a weak source. It is a weak source that the analyst forgot was weak by the time the assessment landed on the principal's desk. The ledger is the discipline that prevents that — the source grade follows the claim into the synthesis, into the red-team review, and into the final product. Without the ledger, every step downstream is operating on laundered evidence.
