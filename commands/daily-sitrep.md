---
description: Sweep the configured watchlist of named outlets, dedupe against prior runs, cluster by topic, and produce today's morning situation report.
argument-hint: "[optional topic filter]"
disable-model-invocation: true
---

You are a strategic analyst running the morning sweep.

Optional topic filter (use only if provided): **$ARGUMENTS**

## Workflow

0. **Pre-flight check — hard-fail if capability is missing.** Before drafting:
   - Probe execution: `uv run python -c "import feedparser; print('exec-ok')"`.
   - Probe network with a single RSS HEAD request to a known feed.
   - **If either fails, stop and reply:** `/daily-sitrep cannot continue: <execution|network> denied. No sitrep has been produced.` Do not draft a sitrep from training-corpus knowledge. A speculative sitrep is worse than no sitrep — readers expect it to reflect actual feed state today.

1. **Load the watchlist.** Read `config/watchlist.yaml`. If it does not exist, copy `config/watchlist.example.yaml` to `config/watchlist.yaml` and tell the user a default watchlist has been initialised — they should review and edit.

2. **Fetch.** Use `fetching-rss-watchlist`. If a topic argument was provided, filter the configured outlets to those tagged with that topic. Otherwise sweep all outlets.

3. **Dedupe against prior runs.** The skill's `cache/rss_seen.json` is the seen-store. Only items unseen since the last run enter today's sitrep.

4. **Cluster by topic.** Use the watchlist's `topics` configuration plus simple keyword matching on the new items. An item can belong to multiple topics.

5. **Grade and triage.** Each item already carries a `source_grade` and `default_info_grade` from the watchlist YAML. Triage:
   - **Top of page:** items from A/B-graded outlets that are *new today* and that mention a fact, decision, or named actor.
   - **Watching:** items that update an ongoing story (reference an entity already prominent in the seen-store).
   - **Background:** lower-grade or low-relevance items, listed but not foregrounded.
   - **Red flags:** single-source claims that, if true, would be material. Flag for verification with `/verify-claim`.

6. **Produce the sitrep.** One page. Structure:
   - **Date and run window** (last sweep timestamp → now)
   - **Top 3 narratives** with: 1-line summary, source grade, primary URL, indicator if any
   - **Watching** (3–5 items)
   - **Red flags / single-source items needing verification**
   - **Indicators that moved** (cross-reference any indicators-to-watch from prior briefs in `briefs/` if the topic matches)
   - **Quiet today** (topics on the watchlist with no new movement — useful negative information)

## Output

Write to `sitreps/sitrep-<YYYY-MM-DD>.md`. If running a topic-filtered sweep, append a `-<topic>` suffix.

Create the `sitreps/` directory if it doesn't exist.

The sitrep is **idempotent within the day**: running `/daily-sitrep` twice on the same day overwrites with the latest sweep. New items between runs *are* picked up because the seen-store progresses.

## Discipline

- The sitrep is *terse*. One screen. If it doesn't fit, the watchlist is too noisy or the clustering is too granular.
- "Quiet today" is a feature, not filler — readers need to know what *isn't* moving.
- Every item in the top section has a primary URL. If the RSS link goes to a re-report, follow the chain in the next sweep, do not paper over it.
- Source grade visible inline (`(B2)` after each item) so the reader can calibrate without leaving the page.
