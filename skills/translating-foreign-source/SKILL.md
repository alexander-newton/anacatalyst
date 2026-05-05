---
name: translating-foreign-source
description: Use when a load-bearing claim originates in a non-English source — central-bank statement in Turkish, court filing in Russian, official gazette in Spanish, social-media post in Arabic. Triggers include "translate this", "what does this say in [language]", "I think this is in Russian", citing any non-English primary, and any case where the analyst is about to quote from a translation rather than from the original.
---

# Translating a Foreign-Language Source

## Overview

Foreign-language sources are not exotic — they are the normal case for any serious analyst working outside the Anglosphere. The risk is not that translation is impossible; modern machine translation (DeepL, internal LLM) handles most prose at screening quality. The risk is **drift**: the *meaning* of an official statement, a legal text, or a politically loaded social-media post often turns on a word the translator smoothed over. The skill is to read the original whenever the claim is load-bearing, and to make the translation step *visible* in the ledger when the original cannot be read.

**Core principle:** *Machine translation is for screening, not for citation.* Any claim that ends up in an assessment must trace to either the original-language source read by someone who reads that language, or be flagged as translation-pending in the ledger and downgraded accordingly.

## When to Use

- Citing a statement, dataset, or document in a language you are not certain you would read at native speed.
- Reading social-media posts in a non-English script (Cyrillic, Arabic, CJK, Devanagari, Hebrew).
- Reading court filings, gazettes, regulatory notices, central-bank communiqués in their original language.
- Reading a translation produced by another outlet (BBC Monitoring, MEMRI, OE Watch).
- Any case where the original-language source exists and you are tempted to skip past it to a re-report.

**Skip for:**
- English-language original sources (this is not the relevant skill).
- Casual context-only reading where no claim is being extracted.
- Sources where you are *certain* you read the language at native speed and are willing to stake a citation on it.

## The Cardinal Rule

**A translation is part of the analytical question, not part of the answer.**

If a claim that depends on the precise wording of a non-English statement is in your draft, and you read the wording only in translation, then the claim is *unverified at the wording level*. The fix is one of:

1. Read the original. (Usually preferred.)
2. Cite both the original-language URL and the translation, and downgrade the row's info-grade by one pending native-speaker review.
3. Reframe the claim to a level the translation can support — e.g., "Reuters reported that X said Y" rather than "X said Y verbatim".

## False Corroboration via Translation Drift

The single most expensive failure: **two sources that *appear* to corroborate each other but are actually two translations of the same claim.**

Examples:
- A Reuters wire reports "TCMB tightened the corridor"; a Turkish-language tweet says `"hedef aralığı yukarı revize edildi"`. The tweet is *not* corroboration of the wire — both might be re-stating the same TCMB sentence, and the tweet's wording is ambiguous between *corridor* and *inflation-target band*.
- A Russian state-media item and an English-language Russian-state-media translation are one source, not two.
- A think-tank's English-language summary of a Mandarin policy speech is one source (the speech) plus one re-report — not two sources.

**The two-source rule applies to *independent* sources, where independence has to survive the translation step.** A row in the evidence ledger should explicitly state *what was translated, by whom*, and only count translations as independent corroboration when the originals are themselves independent.

## The Workflow

### 1. Identify the original-language source

Before anything else: where does the claim *originate*? Trace the chain of custody. If the claim is in an English-language article that is itself a re-report, find the original-language source the article is paraphrasing.

If you cannot find the original, that is a finding — record it in the ledger row's `notes` and downgrade the row.

### 2. Archive the original

Use `archiving-with-wayback`. The snapshot is of the original-language page, not the translation — the translation is downstream and reproducible from the original.

### 3. Translate for screening

For screening, machine translation is acceptable. DeepL is generally preferred over Google Translate for European languages; both are usable for CJK. Internal LLM translation is acceptable for screening across most languages but exhibits more polish-bias (it smooths politically charged wording).

```python
# Pseudocode — DeepL Pro example
import os, httpx
def translate_for_screening(text: str, target_lang: str = "EN-GB") -> dict:
    r = httpx.post("https://api.deepl.com/v2/translate",
                   data={"text": text, "target_lang": target_lang},
                   headers={"Authorization": f"DeepL-Auth-Key {os.environ['DEEPL_API_KEY']}"},
                   timeout=20)
    return r.json()
```

### 4. Record the translator in the ledger

The ledger row's `notes` column must record:
- That the source is non-English (and the original language).
- Who or what translated it (`DeepL Pro`, `BBC Monitoring`, `internal LLM`, `our analyst <name>`).
- Whether a native-speaker review has been done.

A working format:

```
notes: "Source language: tr. Translation: internal LLM (working gloss). Native review: pending. Translation hazard: 'hedef aralığı' is ambiguous between corridor upper bound and inflation-target band."
```

### 5. Downgrade by one info-grade pending native review

A B-grade source whose load-bearing wording you read only in machine translation is **B3, not B2**. A primary document (A1) read only in translation is **A2 pending native confirmation**. The downgrade is mechanical and applies regardless of how confident the translation feels — confidence is exactly the wrong heuristic for translation drift.

When a native speaker (your colleague, BBC Monitoring, an outlet you trust to translate that language) confirms the wording, the row can be upgraded back. The upgrade is recorded in the ledger row's `notes`: "Native review: confirmed by <X> on <date>".

### 6. Escalate to native review for stakes-grade analysis

If the brief is going to a principal, or to a market participant, or to legal — and the load-bearing wording is in a language nobody on the analyst's side reads at native speed — **stop and find a native speaker** before filing. The 2-hour delay is cheaper than the wrong call.

For stakes-grade analysis where no native speaker is available, the honest output is "the claim is reported in [language X] and not independently verified at the wording level; here is what we can say with that caveat" — not a confident assessment that smuggles the translation past the reader.

## Common Mistakes

| Mistake | Fix |
|---|---|
| Quoting from a translation as if it were the original | Quote from the original; gloss in English in brackets. If you don't have the original, say "as translated by X". |
| Counting two translations of the same claim as two sources | Independence is at the *original* level. Two translations of the same statement is one source. |
| Trusting "verified" status on a non-English social account | Verification is identity-attestation, not accuracy-attestation. The translation hazard still applies. |
| Treating BBC Monitoring / MEMRI / OE Watch as "the source" | They are *translators with editorial framing*. Cite the original they translated, and grade the framing separately. |
| Not naming the translator in the ledger | The translator is part of the chain of custody. Anonymous translation is the same problem as anonymous reporting. |
| Polish-bias from LLM translation | Machine translation tends to smooth politically charged wording. For sensitive sources (state media, hostile-actor channels), have a native speaker review the literal wording. |
| Failing to flag known idiomatic landmines | Some terms cannot be translated cleanly (Russian "compatriots", Chinese "fĕn hóng", Turkish "kepeng" idioms). Flag them in `notes` rather than choosing a smooth English equivalent. |

## Translator Reliability Hierarchy

Loosely, in descending order of reliability for stakes-grade citation:

1. **Native speaker on your team** reading the original. Cited by name in the ledger.
2. **Translator-of-record outlets** with transparent methodology: BBC Monitoring (paywalled, gold standard), OE Watch (US Army FMSO), Russia/Eurasia Daily Monitor (Jamestown Foundation).
3. **Native-speaker outlets republishing in English** (e.g., a Turkish journalist's English-language column) — useful but the column is interpretation, not translation.
4. **DeepL Pro** for European languages, or **internal LLM** for any language — screening only; downgrade pending native review.
5. **Google Translate** — screening only, lower fidelity than DeepL on most language pairs.
6. **MEMRI** — *translator with strong editorial orientation*; cite the original alongside, never alone.

## Cross-References

- `building-evidence-ledger` — the row format that carries the translator-of-record and the downgrade.
- `archiving-with-wayback` — archive the original-language page; the translation is reproducible from the snapshot.
- `strategic-news-analysis` — the source-hierarchy and Admiralty grading scheme this skill applies to non-English sources.
- For visual evidence in non-English contexts (signage in foreign script), pair with `geolocating-imagery`.
