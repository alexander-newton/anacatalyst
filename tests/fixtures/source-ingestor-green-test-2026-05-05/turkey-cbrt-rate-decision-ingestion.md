## Source ingestion: Turkey central bank rate decision

**Window:** 2026-05-04T12:00:00Z → 2026-05-05T12:00:00Z (UTC)
**Sources fetched:** Simulated GDELT artlist (12 items) + 1 TCMB primary URL supplied by analyst (treated as `not located` — no live fetch tool exercised in this run).
**Items ingested / unique after dedup / narrative clusters:** 12 / 5 / 3

### Narrative 1 — TCMB cuts policy rate by 250bp to 32.5%
- **Mentions / unique domains:** 10 / 10
- **Wire-republication:** yes (Reuters wire collapsed across 6 republishers: reutersagency.com, reuters.co.uk, timesofindia.com, straitstimes.com, gulftoday.ae, thenationalnews.com)
- **Source-country distribution:** {US: 1, GB: 1, IN: 1, SG: 1, AE: 2, TR: 1, GB(FT): 1, US(Bloomberg): 1, GB(FT lira): 1}
- **Source-grade distribution:** {A: 0, B: 4, C: 0, D: 0} (Reuters wire B; FT B; Bloomberg B; Hurriyet B — domestic broadsheet)
- **Languages:** {en: 9, tr: 1}
- **Most-recent exemplar:** "Lira falls 4% after TCMB surprise cut" — ft.com (B) — 2026-05-05T08:30:00Z
- **What is claimed (≤80 words, no body quotes):** TCMB reduced the policy rate by 250bp to 32.5%. Move described as a surprise/resumption of easing cycle. Lira reported down ~4% post-decision. Hurriyet (TR-language) carries the same headline figure. No primary TCMB communique fetched in this run.
- **What is established vs reported vs rumoured:** Reported by wire (Reuters) and two quality nationals (FT, Bloomberg) plus Turkish broadsheet — convergent on the 250bp / 32.5% figure. Established pending primary-source check against TCMB press release.
- **Open questions a verifier should resolve:**
  - Confirm 250bp vs 350bp via TCMB primary communique
  - Confirm new rate level (32.5%) and which rate (1-week repo)
  - Confirm market-expectations baseline (was hold consensus?)
  - Verify lira move magnitude against intraday FX data

### Narrative 2 — Cut driven by political pressure ahead of municipal elections
- **Mentions / unique domains:** 2 / 2
- **Wire-republication:** no
- **Source-country distribution:** {US: 1, GB: 1}
- **Source-grade distribution:** {A: 0, B: 2, C: 0, D: 0} (WSJ B; FT B — both quality national, but underlying sourcing is anonymous/interpretive)
- **Languages:** {en: 2}
- **Most-recent exemplar:** "Turkey rate cut driven by political pressure ahead of municipal elections, sources say" — wsj.com (B) — 2026-05-05T08:35:00Z
- **What is claimed (≤80 words, no body quotes):** WSJ cites unnamed sources attributing the cut to political pressure ahead of upcoming municipal elections. FT framing ("Erdogan turns the screw … election-eve") is editorially aligned but does not independently corroborate the sourcing chain.
- **What is established vs reported vs rumoured:** Reported, not established. Anonymous-sourced claim in WSJ; FT framing is interpretive. Caps at info-grade 3 absent named corroboration.
- **Open questions a verifier should resolve:**
  - Date and scope of the referenced municipal elections
  - Any on-record statement from TCMB governor or Treasury
  - Whether opposition or independent economists are quoted on the record

### Narrative 3 — Unverified social claim: cut was actually 350bp, communique to be amended
- **Mentions / unique domains:** 1 / 1
- **Wire-republication:** no
- **Source-country distribution:** {US: 1} (geolocation per GDELT; X user nationality unverified)
- **Source-grade distribution:** {A: 0, B: 0, C: 0, D: 1}
- **Languages:** {en: 1}
- **Most-recent exemplar:** "BREAKING: I'm hearing the actual cut was 350bp not 250bp…" — x.com (D) — 2026-05-05T08:18:00Z
- **What is claimed (≤80 words, no body quotes):** Anonymous EM-commentator account asserts the actual cut was 350bp and the communique will be amended. Directly contradicts wire/quality-national reporting.
- **What is established vs reported vs rumoured:** Rumour. Single anonymous social post, contradicted by convergent B-grade reporting and not corroborated elsewhere in the artlist.
- **Open questions a verifier should resolve:**
  - Does the TCMB communique state 250bp or 350bp?
  - Has any amendment been published?
  - Account track record / prior accuracy

### Evidence-ledger rows
```csv
claim,source,source_grade,info_grade,primary_url,archive_url,accessed_at,notes
TCMB cut policy rate by 250bp to 32.5% on 2026-05-05,Reuters wire,B,2,https://reutersagency.com/news/turkey-cbrt-cuts-250bp,not located,2026-05-05T08:02:00Z,"Wire collapsed across 6 republisher domains (reutersagency.com, reuters.co.uk, timesofindia.com, straitstimes.com, gulftoday.ae, thenationalnews.com); cosine ≥ 0.85 on title. Attributed to Reuters, not republishers."
TCMB cut policy rate by 250bp to 32.5%,TCMB press release,A,2,https://www.tcmb.gov.tr/wps/wcm/connect/EN/TCMB+EN/Main+Menu/Announcements/Press+Releases/Press+Releases-2026,not located,2026-05-05T12:00:00Z,"Primary URL supplied by analyst; not fetched in this run. Verifier must open and confirm size/level/rate-type. Info-grade held at 2 pending fetch."
TCMB cut policy rate by 250bp,Hurriyet (TR-language broadsheet),B,2,https://hurriyet.com.tr/ekonomi/merkez-bankasi-faiz-indirimi,not located,2026-05-05T08:01:00Z,"Turkish-language domestic coverage; corroborates wire on size. Translation of headline only — body not ingested."
Lira fell ~4% after the decision,Financial Times,B,3,https://ft.com/content/def456,not located,2026-05-05T08:30:00Z,"Single quality-national source for FX move magnitude; verify against intraday FX data (Bloomberg/Refinitiv tick) before citing."
Cut framed as surprise resumption of easing cycle,Bloomberg,B,3,https://bloomberg.com/news/articles/turkey-easing-cycle,not located,2026-05-05T08:25:00Z,"Editorial framing; 'surprise' implies prior consensus for hold but consensus not separately sourced here."
Cut driven by political pressure ahead of municipal elections,Wall Street Journal (citing unnamed sources),B,3,https://wsj.com/articles/turkey-cuts-rates-political-pressure,not located,2026-05-05T08:35:00Z,"Anonymous sourcing within a B-grade outlet; carry as 'if true' colour. FT headline framing aligned but not independent corroboration."
Election-eve political-pressure framing,Financial Times,B,3,https://ft.com/content/abc123,not located,2026-05-05T08:20:00Z,"Editorial framing rather than independent reporting; do not double-count with WSJ row."
Claim that actual cut was 350bp and communique will be amended,Anonymous account @em_commentator on X,D,4,https://x.com/em_commentator/status/...,not located,2026-05-05T08:18:00Z,"Single anonymous social post; contradicts convergent B-grade reporting. Capped at D3 by rule; downgraded to D4 because contradicted by primary-adjacent sources. Discard unless corroborated."
```

### What I did not fetch
- TCMB primary press release body (URL supplied; not opened in this run — info-grade for the size claim cannot rise to 1 until fetched).
- Article body text for any item (by design — metadata-only ingestion).
- Intraday lira FX tick data to verify the ~4% move.
- Prior-meeting TCMB communique / rate path for trend context.
- Analyst consensus (Bloomberg/Reuters poll) baseline for "surprise" framing.
- Track record / prior accuracy of @em_commentator account.
- Municipal-election calendar / scope referenced in WSJ political-pressure framing.
- Non-Turkish, non-English domestic coverage (e.g. Sabah, Daily Sabah, Cumhuriyet) — only one TR item in artlist.

### Methodology trail
- **Dedup method:** domain → wire-collapse (cosine ≥ 0.85) → narrative-cluster (TF-IDF cosine ≥ 0.6)
- **Pitfalls flagged:**
  - Reuters wire collapsed 6→1; republisher count preserved in notes to avoid inflating apparent independence.
  - FT carries two distinct items (political framing + lira move) — kept as two rows; not double-counted as corroboration of WSJ political-pressure claim.
  - Hurriyet headline-only ingestion; Turkish body not parsed — translation drift risk on any claim beyond the headline figure.
  - TCMB primary URL marked `not located` honestly; this is the single highest-leverage fetch the verifier should perform first.
  - X post capped at D and downgraded to info-grade 4 due to direct contradiction with convergent B-grade reporting; do not treat as a live hypothesis.
  - `sourcecountry` for x.com is GDELT best-effort and unreliable for social platforms.
  - "Surprise" framing in Bloomberg/FT is not independently sourced to a consensus poll within the artlist.
