# searching-web-with-operators RED test — 2026-05-05

**Note:** this fixture preserves the **RED** baseline (skill *not* loaded). A separate GREEN run was not conducted because the same WebSearch/WebFetch tool-block that has surfaced across earlier GREEN tests would have made the comparison uninformative — both runs would fall back to training-corpus knowledge.

## Test scenario

A multi-step OSINT discovery task: locate the primary text of Argentine Ley 27.541 (the "PAÍS tax", December 2019), identify the article(s) establishing the 30% surcharge, and verify whether the surcharge applied to *outward portfolio investment*. Designed to require operator-driven search (`site:infoleg.gob.ar`, `filetype:pdf`, exact-phrase quoting on the law number).

## Baseline behaviour

The unbriefed agent was tool-blocked but described the queries it would have run:

- `Ley 27.541 ... InfoLEG ... articulo 35`  — used InfoLEG site identifier ✅
- `"Ley 27541" "impuesto PAIS" "30%" Boletin Oficial` — quoted phrases + authoritative domain ✅

So *implicit* operator usage is decent unprompted. The substantive deliverable was high-quality — correctly identified that the PAÍS tax did **not** directly target outward portfolio investment (it's a retail consumption + hoarding surcharge), and flagged the brief's premise as a conceptual conflation between the tax instrument (Art. 35–44 of Ley 27.541) and the underlying MULC access prohibition (BCRA Comunicación "A" series).

## What was missing without the skill

- **No engine cross-check.** Both queries described as Google-only; no Yandex mention despite the topic being a Latin American statute where Yandex's older-content advantage might matter.
- **No methodology trail.** Query string, engine, position, personalisation status — none recorded in a ledger-ready form.
- **No translate-keywords-first discipline.** Queries mixed Spanish and English without explicit foreign-language framing.

## What the skill adds

These three gaps are the skill's mechanical value-add:

1. The **cross-engine table** (Google + Yandex + Bing depending on language and topic) — explicit recipe.
2. The **methodology trail** rule — query string, engine, position go in evidence-ledger `notes`.
3. The **translate-keywords-first** rule — translate keywords to the source language before querying, run both queries.

Plus a recipe table that makes operator combinations canonical for common analyst tasks (find-the-statute, find-the-leak, find-content-before-date, find-dissenting-analysis).

## Carried-forward observation

Six straight GREEN/RED tests now where the WebFetch/WebSearch tool-block has been the operative constraint. This skill is the one most directly affected — its whole value rests on making search reproducible and methodical, and we have not been able to demonstrate that empirically. **Hard regression test will need to wait for a session where Claude has WebSearch/WebFetch in its allow-list.**

The skill itself is shipped (and structurally consistent with the rest of the suite); the regression baseline is provisional pending an unblocked test environment.
