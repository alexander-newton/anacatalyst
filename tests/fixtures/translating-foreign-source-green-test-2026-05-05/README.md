# translating-foreign-source GREEN test — 2026-05-05

Output produced by the GREEN test of the `translating-foreign-source` skill, comparing behaviour against the RED baseline (no skill loaded).

**Test scenario:** a Turkish-language tweet from a verified-status financial commentator (`@tr_macro_handle`) plus a Reuters wire item, both reporting on a TCMB rate decision. The Turkish phrase `hedef aralığı` is genuinely ambiguous between "rate corridor bound" and "inflation-target band" — different policy actions with different implications. The agent has 8 minutes and no native Turkish speaker.

## Baseline behaviour (RED, no skill)

The unbriefed agent already exhibited most of the discipline this skill encodes:
- Translated as "working gloss" with explicit unconfirmed flag
- Identified the `hedef aralığı` ambiguity unprompted
- Refused to count the tweet as Reuters corroboration
- Used the phrase "false corroboration via translation drift" verbatim, unprompted
- Graded the tweet C3, Reuters B2

This was actually so strong that I borrowed the agent's "false corroboration via translation drift" phrasing as the canonical name for the failure mode in the skill.

## Skill-driven improvements (GREEN)

The skill produced concrete behavioural deltas over the strong baseline:

1. **Tweet info-grade tightened C3 → D3.** The skill's mechanical rule "anonymous social media caps at D" held. Verified status was correctly noted as "identity-attestation, not accuracy-attestation" — a phrase from the skill body.
2. **Source language explicit in `notes`** ("SOURCE LANGUAGE: Turkish") rather than implicit.
3. **Translator-of-record named** ("Translation: working gloss only; no native speaker available") rather than implicit.
4. **Translation hazard tagged as load-bearing** ("Translation hazard — load-bearing: *hedef aralığı* is ambiguous between…").
5. **False-corroboration cited as a named failure mode** ("counting them as corroboration is exactly the false-corroboration failure mode the skill exists to prevent") rather than as an observation.
6. **Editorial-vs-claim separation explicit** ("*Lira için kötü değil* is editorial colour, not fact").

The skill also drove the agent to write a separate CSV file at `evidence/turkey-monetary-policy-2026-05-05.csv`, applying `building-evidence-ledger`'s "must be a separate artefact" rule.

## Why this matters — the marginal-improvement argument

This is the second skill (after `fetching-news-gdelt`) where the unbriefed-Claude baseline was already strong. The pattern is consistent: the parent skills (`strategic-news-analysis`, `building-evidence-ledger`) teach the *attitude*; the specialist skills add **mechanical rules** that prevent the discipline from eroding under load.

A Claude with strong baseline judgement might apply the right grade once. A Claude with the skill loaded will apply the right grade *consistently* across 50 ledger rows in a long brief, because the rule is mechanical and the failure mode is named. That consistency is what the skill is buying.

This fixture is the regression baseline. Future re-runs of the same scenario should produce comparably-tightened grades, the same six explicit-annotation deltas, and the same canonical "false-corroboration" framing.
