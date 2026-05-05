# TDD baseline pass — live verification — 2026-05-05

Second TDD baseline run, this time with broad WebFetch + Bash permissions in `.claude/settings.local.json`. Same topic as the prior tool-blocked run (`tests/fixtures/tdd-baseline-2026-05-05/`), deliberately, so the two fixtures form a before/after pair showing what live verification adds.

**Topic:** Recent OFAC designations targeting Russia's shadow-fleet oil tankers — scope, effectiveness, second-order EU energy-security impacts.

## Outcome

Pre-flight passed. All six fetcher skills ran live. **17 of 17 ledger rows have a real `primary_url`** — the headline metric for whether live verification actually delivered. Credential audit clean across 32 artefacts (brief, ledger, 14 scratch scripts including the `_safe.py` redaction wrapper).

## Why this fixture matters — what live verification changed

Comparing the prior inference-grade brief against this live-verified version on the same topic surfaces six material corrections:

| Claim | Prior (inferred) | Live | Effect |
|---|---|---|---|
| Russia-program vessel count | "several hundred" (C3) | **448 vessels, 215 specifically tankers** (A1) | Specificity shift |
| EU imports of HS27 from Russia | "~€140bn (2022) → €20bn (2024)" (B2) | **$155bn → $32bn → $24bn** by year (A1) | Shape right; precision now primary-document |
| Brent crude level Q1–Q2 2026 | "$65–$85/bbl band" (B3 inference) | **$113.89/bbl on 27 April; April monthly avg $116** (A1) | **Frame-changing $30–40/bbl miss** |
| OFAC tempo | "steady continued tranches" assumed | **1 of 9 recent actions on Russia; 4 are Iran** | Bandwidth has rotated to Iran-Hormuz |
| Kinetic enforcement | not mentioned | Ukraine struck 3 tankers + Novorossiysk port ~3 May; Sweden seized a shadow-fleet tanker with a Chinese captain ~3-4 May | Entire new enforcement vector |
| Named vessels | none | LINDA, PEGAS, POLAR ROCK; **8 distinct Sovcomflot/SCF SDN entries**, cross-verified at score 1.00 against OpenSanctions | Specific evidence vs hand-waving |

The Brent-level miss is the load-bearing one. It moves the bottom-line framing from "Russia-shadow-fleet enforcement is the dominant variable for EU energy security" (prior) to "the Persian Gulf risk premium dominates; Russia-shadow-fleet enforcement is second-order and the active channel is now EU coastal-state seizure plus Ukrainian kinetic strikes" (live). A principal acting on the prior inference brief would have been positioned for the wrong story.

This fixture is the empirical case for the **hard-fail-on-missing-permissions** discipline: an inference brief looks polished, has calibrated bands, has a structured ledger — but quietly assumes a baseline that is wrong by 50%. The discipline that says "stop, refuse, demand verified data" prevents exactly this class of failure.

## Bugs surfaced and applied to skills

Three concrete fixes shipped to `skills/` in this round:

1. **`fetching-ofac-sanctions`** — The skill documented an RSS feed at `recent-actions/recent-actions-rss-feed`. **404 as of 2026-05-05.** The HTML page at `https://ofac.treasury.gov/recent-actions` is the working surface. Skill updated.
2. **`fetching-comtrade-trade`** — `reporter=918` (documented as EU27) returns **0 rows** from the live `/data/v1/get/C/A/HS` endpoint. The working code is `reporter=97` ("European Union"). Skill updated.
3. **`fetching-comtrade-trade`** — Each query returns **multiple `customsCode` rows** per (reporter, partner, commodity, period, flow) tuple: `C00` is total; `C01`/`C06`/`C20` are subsets. Naive `df["primaryValue"].sum()` triple-counts. The `comtrade_get` helper now defaults to `customs_code="C00"` and the skill documents the gotcha.

## Files

- `russia-shadow-fleet-ofac-2026-05-05.md` (19,727 bytes) — the BLUF brief; ten sections per `producing-deep-brief`
- `russia-shadow-fleet-ofac-2026-05-05.csv` (10,396 bytes) — 17-row evidence ledger, all rows with real primary URLs
- `scratch/` — 14 runnable scripts written by the agent during the run:
  - `_safe.py` — credential-redaction helper (URL sanitisation, `safe_get` wrapper)
  - `fetch_{ofac,fred,eia,comtrade,gdelt,opensanctions,ofac_recent}.py` — per-skill live fetches
  - `probe_{comtrade,comtrade2,ofac_rss}.py` — diagnostic probes that surfaced the bugs
  - `analyse_sdn_russia.py`, `gdelt_cluster.py`, `comtrade_canonical.py`, `oil_price_context.py` — analytical scripts that fed the brief

## Re-running

```bash
# from the plugin root
uv run python tests/fixtures/tdd-baseline-live-2026-05-05/scratch/fetch_eia.py
# etc.
```

All scripts use the `_safe.py` redaction helper and confirm key presence by length only.

## Pair this fixture with...

`tests/fixtures/tdd-baseline-2026-05-05/` — the prior tool-blocked run on the same topic. The two together show what the system produces under the two operative permission regimes, and why the user's hard-fail policy (refuse rather than degrade) is the right default.
