# /strategic-brief GREEN test — 2026-05-05

Output produced by the GREEN test of the `/strategic-brief` slash command's wiring.

**Test scenario:** Argentina announces a unilateral 30% capital-flow surcharge on outward portfolio investment. Single uncorroborated wire-style seed paragraph. No external fetch tooling available (WebFetch / WebSearch / Bash external calls all permission-blocked).

**What the test was checking:** that the multi-step orchestration the command's prompt body specifies actually fires the right skills in the right order — provenance → fetch → ledger → lens triage → synthesis → red-team → two artefacts in the right paths.

## Result

The command's wiring held under tooling adversity. The agent:

- **Built the ledger first** — 16 rows, mostly graded F6/D5 because the seed couldn't be corroborated. Critically, the *only* A1 row is a meta-fact about the tooling gap itself (a verifiable claim about its own environment).
- **Led the BLUF with the verification gap** — "low confidence on the baseline factual claim itself" was the headline, not a bottom-of-page caveat. This is the building-evidence-ledger discipline working as designed.
- **Triaged lenses cleanly:** public finance + economic + political + historical engaged; demographic, geographic, military dropped out with reasoning.
- **Red-team moved calibration:** KJ-3 confidence stepped down moderate → low-moderate, KJ-4 band widened, two indicators added that weren't in the draft.
- **Generated 14 indicators** with thresholds and time horizons (T+5 / T+30 / T+90 / T+180), comfortably above the three-indicator floor.

## Structural findings to address elsewhere

These are *plugin-level* gaps the command exposed, not skill-level bugs:

1. **External fetch tooling blocked.** Recurring across GREEN tests. The fix lives in agent specs (#8 lens-applier, #9 source-ingestor) — those need `WebFetch` in their tool allow-list. Without it, fetch skills become reference-only.
2. **`config/watchlist.yaml` does not exist.** The `fetching-rss-watchlist` skill says to degrade gracefully, which the agent did, but the project should ship with `config/watchlist.example.yaml` as a starter (task #19).
3. **Knowledge cutoff drift.** Jan 2026 cutoff vs May 2026 assignment date. Real fix is enabling the fetch tooling so live data closes the gap.

These fixtures are kept as regression baselines: future re-runs of `/strategic-brief` on a comparable seed should produce comparably-structured output. If they don't, the command has regressed.
