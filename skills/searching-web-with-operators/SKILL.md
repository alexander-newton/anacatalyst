---
name: searching-web-with-operators
description: Use when you need to find a specific document, primary source, or piece of evidence on the open web — not aggregated news. Triggers include "find the original", "find the law text", "find what X said on Y", "filetype PDF", "site search", any case where a vague query returns re-reports instead of primaries, and any case where the obvious search has failed.
---

# Searching the Web with Operators

## Overview

Web search is the OSINT analyst's most-used tool — and the most underused at expert level. A bare query ("Argentina PAÍS tax") returns aggregator chains. The same question rephrased with operators (`site:infoleg.gob.ar "27541" filetype:pdf`) lands on the statute text in one click. The skill is the operator vocabulary plus the discipline of running parallel queries on multiple engines, because **Google personalises, Yandex remembers what Google forgets, and "no results" rarely means absence**.

**Core principle:** *The operator is the methodology.* Every consequential search should be reproducible by another analyst pasting the query into the same engine. "I Googled it" is not a method.

## When to Use

- Locating the **primary source** of a claim (statute, court filing, central-bank statement, dataset).
- Searching **specific domains** for content (a regulator's site; an outlet's archive).
- Finding content **in a specific time window** ("what was published before X date about Y").
- Searching for **non-Western content** where Google de-prioritises non-English results.
- Verifying that something *doesn't* exist — but only after multi-engine, multi-language queries.

**Skip for:**
- Bulk topic monitoring at scale — `fetching-news-gdelt` is the right tool there.
- Real-time wire monitoring — `fetching-rss-watchlist`.
- Looking up *known* URLs you can fetch directly.

## The Operator Vocabulary

These work on Google. Most also work on Bing and Yandex (with minor variants noted).

| Operator | Effect | Example |
|---|---|---|
| `site:domain` | Restrict to a domain or TLD | `site:gov.tr`, `site:.go.jp` |
| `-site:domain` | Exclude a domain | `-site:wikipedia.org` |
| `intext:phrase` | Phrase must appear in body | `intext:"primary surplus"` |
| `intitle:phrase` | Phrase must appear in page title | `intitle:"annual report"` |
| `inurl:phrase` | Substring must appear in URL | `inurl:press-release` |
| `filetype:ext` | Restrict to file extension | `filetype:pdf`, `filetype:xlsx`, `filetype:csv` |
| `"exact phrase"` | Exact-match (mandatory in modern Google to defeat fuzzy expansion) | `"capital flow management"` |
| `before:YYYY-MM-DD` | Indexed-before date | `before:2024-01-01` |
| `after:YYYY-MM-DD` | Indexed-after date | `after:2023-06-01` |
| `OR` (uppercase) | Boolean OR | `(Putin OR Putín)` |
| `(...)` | Group | `(IMF OR "World Bank") AND Argentina` |
| `*` | Wildcard inside a quoted phrase | `"the * minister said"` |
| `+term` | (Removed by Google but still works on Yandex) Force inclusion | `+RUB` |
| `~term` | (Removed by Google but still works on Yandex) Synonym expansion | `~devaluation` |

**Yandex-specific extras:**
- `lang:ru` / `lang:tr` / `lang:en` — language filter (where Google's `&lr=lang_ru` is a URL parameter, not an operator).
- `mime:pdf` (instead of `filetype:`).
- `date:20230101..20231231` (date range as a single operator).

**Bing-specific extras:**
- `feed:` — sites that publish a named feed.
- `hasfeed:` — sites that have any feed at all.
- `contains:filetype` — pages linking to that filetype.

## Engine Selection — Which to Run, When

The most expensive search mistake is **single-engine reliance**. Run at least two engines for any consequential query, and a third for non-Western content.

| Topic | Default | Cross-check | Why |
|---|---|---|---|
| English-language Western government / corporate / academic | Google | Bing or DuckDuckGo | Google has the deepest English Western index; Bing sometimes catches what Google has dropped. |
| Russian, Ukrainian, Belarusian, Central Asian content | **Yandex first**, then Google | Bing | Yandex indexes content Google de-prioritises post-2022, including mirrored / archived older content. |
| Turkish, Caucasian content | Yandex | Google | Yandex has stronger Turkish-language coverage than Google for older content. |
| Chinese content | Baidu (with caveats — heavy state filtering) | Yandex | Google is blocked in China; Bing is partially indexed; Baidu reflects what's permitted on the Chinese internet. |
| Japanese content | Google | Yahoo Japan | Yahoo Japan has historically had different ranking from Google JP. |
| Korean content | Google | Naver | Naver has stronger Korean-language indexing. |
| Older content / archived versions of dropped pages | Wayback Machine + Yandex | Google `cache:` (limited) | Yandex's "cached version" tends to outlast Google's. |
| Sensitive content / personalisation-prone topics | DuckDuckGo + Brave Search | Google | No personalisation; Brave has its own independent index growing since 2023. |

## Recipes — Patterns That Pay Off

### Find the primary text of a named law / statute

```
site:infoleg.gob.ar OR site:boletinoficial.gob.ar "27.541" filetype:pdf
site:legifrance.gouv.fr "loi n° 2024-XXX" filetype:pdf
site:congress.gov "Public Law 117-XX"
site:eur-lex.europa.eu "Regulation (EU) 2024/XXX"
```

The pattern: **(authoritative gov domain) + (exact statute number) + (filetype if a PDF is canonical)**.

### Find a leaked / referenced document by exact phrase

```
"<a distinctive sentence quoted in the news>" -site:nytimes.com -site:wsj.com
```

If the news report quoted the document, the document text is somewhere on the open web. Quote a *distinctive* sentence — long enough to be unique, short enough to survive minor whitespace differences.

### Find what an outlet published before / after a date

```
site:ft.com "topic" before:2024-03-15 after:2024-03-01
site:reuters.com inurl:turkey before:2026-05-06 after:2026-05-04
```

### Find dissenting / non-mainstream analysis

```
"<topic>" -site:wsj.com -site:ft.com -site:bloomberg.com -site:nytimes.com -site:reuters.com -site:bbc.com -site:cnn.com
```

Discards the wires/quality-press; surfaces think-tank, academic, and partisan analysis.

### Find regulatory filings on a topic

```
(site:sec.gov OR site:fca.org.uk OR site:bafin.de OR site:cnmv.es) "<topic>"
```

### Find an older version of a deleted page

If Google says "no results" and the page is suspected dropped:

1. Try the same query in Yandex.
2. Try the URL in `https://web.archive.org/web/*/<URL>`.
3. Try `cache:<URL>` (limited; mostly removed from Google).
4. Try `archive.today/<URL>`.

### Find foreign-language content for which the analyst only has English keywords

Translate the keyword to the original language *first*, then search:

```
# Bad
site:.tr "central bank rate cut"

# Better
site:.tr "Merkez Bankası faiz indirimi"
site:.tr "TCMB faiz" filetype:pdf
```

For consequential searches, run both queries — sometimes English-language pages on a `.tr` domain are themselves the find.

### Find an academic paper / preprint

```
site:arxiv.org "<topic>"
site:papers.ssrn.com "<topic>"
"<distinctive phrase>" filetype:pdf -site:wikipedia.org
```

## Pitfalls

| Pitfall | Why | Fix |
|---|---|---|
| Single-engine search | Personalisation + index gaps | Always 2+ engines; 3 for non-Western or sensitive. |
| Trusting "no results" | "No results" usually means "not on this engine in your locale" | Switch engines; switch language; switch operator combinations; check Wayback. |
| Not quoting | Modern Google fuzzes phrases aggressively | `"exact phrase"` for anything multi-word that matters. |
| Ignoring `before:`/`after:` | Search-engine ranking biases recent content | Pin a window for any historical search. |
| Using English keywords for foreign content | Google de-ranks non-English even on `.tr` / `.ru` domains | Translate keywords first; pair both queries. |
| Counting result counts as evidence | The "About 250,000 results" number is not a real count and is heavily approximated | Don't cite it. Look at the top results. |
| Search-engine personalisation drift | Two analysts running the same query get different results | DuckDuckGo or incognito browser; or document the result set you used. |
| Quoting from snippet | Snippets are truncated and sometimes machine-translated | Always click through and read the full page. |

## Discipline — What Goes in the Evidence Ledger

For any search-derived citation, the evidence-ledger row's `notes` column should record:

- **The query string** (verbatim, including operators).
- **The engine used** (Google, Yandex, Bing, DDG).
- **The position of the cited result** (top hit, page 2, etc.).
- **Whether the search was personalised** (incognito vs logged-in).
- **The translated query if foreign language** ("queried both *capital flow management* and Spanish *gestión de flujos de capital*").

The query is the methodology. Without it, "I Googled it" is what you're admitting to.

## Common Mistakes

| Mistake | Fix |
|---|---|
| "Google it" as a methodology | Specify operators; specify engine; record the query. |
| Treating page 1 of Google as the universe | Most consequential primaries sit on page 2–5; ranking is for popular consumption, not for analysts. |
| Stopping at the snippet | Fetch the page; read it. Snippets lie. |
| Ignoring Yandex | Reflexive choice for any post-2022 Russian-language content. |
| Using `cache:` and assuming it works | Google has been deprecating it; use Wayback. |
| Not de-Anglicising the query | Translate keywords to the source language for non-Western primaries. |
| Forgetting `filetype:pdf` | Most primary documents (statutes, regulations, IMF reports, central-bank papers) are PDF. The `filetype:` operator alone often surfaces what bare queries hide. |
| Trusting Google's date filter implicitly | The dates are inferred from page metadata that lies. Cross-check by reading the page. |

## Cross-References

- Output rows feed `building-evidence-ledger`. Record the **query string** in `notes`; that is the reproducible methodology.
- For pages that have been edited or deleted, pair with `archiving-with-wayback` — the operator search finds the URL, Wayback preserves what was there.
- For non-English search, pair with `translating-foreign-source` for the translation discipline on what you find.
- For specific data products (bilateral trade, sanctions, conflict events, energy data), prefer the dedicated fetcher skills — search is for *discovery*, structured fetchers are for *retrieval at scale*.
- Claude's built-in `WebSearch` tool is the default execution path; the `googlesearch-python` library is a free fallback for batch use, and SerpAPI / Bing Web Search API are paid options when scale demands them.
