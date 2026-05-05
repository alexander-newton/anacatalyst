---
name: producing-daily-sitrep
description: Use when assembling a one-page morning situation report from a watchlist sweep. Triggers include "produce the sitrep", "morning brief format", "daily wrap", "what's on the watchlist today", and any case where new RSS items + cross-run dedup state must be turned into a terse, source-graded one-pager.
---

# Producing a Daily Sitrep

## Overview

A daily sitrep is the **canonical output format** of the `/daily-sitrep` command. It is a one-screen summary of what moved on the watchlist since the last sweep, with source grades inline and indicators cross-referenced against any open briefs.

**Core principle:** *The sitrep earns its place by being terse and consistent.* Readers scan it the same way every morning — they know where to find new wire claims, where to find single-source items needing verification, and where to find what *isn't* moving. Departing from the format breaks the routine and the document becomes prose.

## When to Use

- Producing the deliverable from `/daily-sitrep` (whether full-watchlist or topic-filtered).
- A weekly equivalent — same shape, longer window — when daily cadence is too granular.

**Skip for:**
- Deep dives — use `producing-deep-brief`.
- Single-claim verifications — `verify-claim` is its own format.

## The Format

A daily sitrep is a single markdown file at `sitreps/sitrep-<YYYY-MM-DD>.md` (with optional `-<topic>` suffix for filtered runs). One screen. Idempotent within the day.

```markdown
# Daily sitrep — <YYYY-MM-DD>

**Window:** <last sweep ts> → <now>
**Outlets swept:** <N> (<list of names>)
**New items / unique narratives:** <N> / <K>

## Top of the page

Items from A/B-graded outlets that are *new today* and that mention a fact, decision, or named actor. Source grade visible inline as `(A1)` / `(B2)` / `(C3)` after each item, so the reader can calibrate without leaving the page.

- **<one-line summary>** *(A1)* — <primary URL>. <one-line indicator if applicable: "I-3 from turkey-cbrt brief: lira move > 4% threshold breached.">
- **<one-line summary>** *(B2)* — <URL>.
- **<one-line summary>** *(B2)* — <URL>.

## Watching

Items that update an ongoing story — same entity / topic that's prominent in the seen-store from prior runs. Background, not foregrounded.

- <one-liner with grade and URL>
- <…>
- <…>

## Red flags

Single-source claims that, *if true*, would be material. Each one is a candidate for `/verify-claim` follow-up.

- *(B3)* <claim> — <outlet> — <URL> — verify against: <what would corroborate it>.
- *(D4)* <claim> — <outlet> — <URL> — anonymous or social-media; corroboration required before any downstream use.

If empty, write `None today.` rather than removing the section.

## Indicators that moved

Cross-reference any indicators-to-watch from open briefs in `briefs/` if today's items match. Each entry names the brief, the indicator, and what moved.

- *<brief topic>* — Indicator I-<n> "<threshold>" — observed: <value>. Status: **breached / approaching / inverted**.
- <…>

If no open briefs, write `No open briefs cross-referenced.`.

## Quiet today

Topics on the watchlist with no new movement since the last sweep. *Useful negative information* — the reader needs to know what *isn't* changing.

- <topic name>: <last item observed: date / outlet>.
- <topic name>: no items in the last <N> days.

## Methodology trail

- **Sweep query / topic filter:** <verbatim>
- **Dedup state:** <N items in seen-store before this run; <K> added in this run>
- **Outlets that returned errors / 304-not-modified:** <list>
- **Pitfalls:** <e.g. "Reuters feed appeared to drop the geopolitics tag this morning — re-check tomorrow">
```

A worked sitrep is built by the `/daily-sitrep` command in concert with `fetching-rss-watchlist`.

## Quick Reference

| Element | Done well | Done badly |
|---|---|---|
| Length | One screen, ~30–50 lines | Multi-page narrative |
| Source grades | Inline `(A1)` / `(B2)` after every item | Buried in a footer |
| Top of the page | A/B-graded *new* items only | Mixed grades; old items |
| Red flags | Single-source claims, with what would corroborate | Anything alarming-sounding |
| Indicators | Cross-referenced to open briefs by name | Generic "watch this" |
| Quiet today | Listed topic-by-topic | Omitted |
| Methodology trail | Query, dedup state, errors, pitfalls | Skipped |

## Common Mistakes

| Mistake | Fix |
|---|---|
| Sitrep balloons past one screen | The watchlist is too noisy or the clustering is too granular — tighten upstream, not by truncating. |
| Source grades absent | Inline `(grade)` after every item. The watchlist YAML already encodes them. |
| "Quiet today" omitted | Negative information is information. Always include the section. |
| Red flags conflated with top-of-page | Red flags are *single-source* and would be material *if true*. Top-of-page is corroborated. |
| Indicators referenced without naming the brief | Indicator without a brief reference is a free-floating claim. Cite by topic + indicator number. |
| Re-running the sitrep produces a different file | The sitrep is idempotent within the day. Same `<YYYY-MM-DD>` filename; latest sweep overwrites. |
| Methodology trail skipped | Without it, tomorrow's analyst doesn't know what changed: which feeds errored, which keywords drifted. |

## Cross-References

- Items are produced by `fetching-rss-watchlist`. Each comes pre-graded from the watchlist YAML.
- Red-flag items are candidates for `verify-claim` follow-up.
- Indicators in the "Indicators that moved" section come from open `briefs/<topic>-<date>.md` files produced by `producing-deep-brief`. The cross-reference is what turns a sitrep into a *living monitoring product*.
