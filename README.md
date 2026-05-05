# strategic-analyst

A Claude Code plugin that turns the assistant into a disciplined open-source intelligence analyst.


---

## Quick start (10 minutes)

```bash
# 1. Get dependencies
uv sync                                   # installs from pyproject.toml + uv.lock

# 2. Set up secrets
cp .env.example .env
chmod 600 .env
# edit .env and fill in at least FRED_API_KEY (see "API keys" below)

# 3. Install the plugin into Claude Code
/plugin marketplace add /path/to/this/dir
/plugin install strategic-analyst@local

# 4. Try a slash command
/strategic-brief Argentina capital controls — what's the call?
```

If you're not sure what's working, the SessionStart hook reports which keys are set and which aren't every time you start Claude Code in this directory.

---

## Installation

### Local development (recommended for first install)

From the directory *containing* this plugin folder:

```bash
/plugin marketplace add /absolute/path/to/claude-strategic-analysis
/plugin install strategic-analyst@local
```

Skill descriptions appear immediately. Reload Claude Code to pick up edits.

### From a public marketplace

Publish this repo to GitHub, register a marketplace pointing at it, then:

```bash
/plugin marketplace add github:<your-user>/strategic-analyst-marketplace
/plugin install strategic-analyst
```

### Sideload (for hacking)

Symlink this folder into `~/.claude/plugins/` and add the path to `~/.claude/plugins/installed_plugins.json`. Useful for development; not recommended for distribution.

---

## Permissions

The plugin's fetch skills need to make HTTP calls and run Python. Claude Code asks for permission per tool call by default. To run the workflow without per-call prompts, add allows to `.claude/settings.local.json` (project-local, gitignored). The shipped `.claude/settings.local.json.example`-style block is reproduced below — copy what you want into your own `.claude/settings.local.json`:

```json
{
  "permissions": {
    "allow": [
      "Read(//<your-claude-dir>/**)",

      "Bash(uv run *)",
      "Bash(uv run python *)",
      "Bash(ls *)", "Bash(pwd)", "Bash(cat *.md)",
      "Bash(head *)", "Bash(tail *)", "Bash(wc *)",
      "Bash(grep *)", "Bash(find *)",
      "Bash(mkdir -p *)",
      "Bash(rm -f tests/scratch/*)", "Bash(rmdir tests/scratch)",

      "WebFetch(domain:api.stlouisfed.org)",
      "WebFetch(domain:api.eia.gov)",
      "WebFetch(domain:www.sec.gov)",
      "WebFetch(domain:data.sec.gov)",
      "WebFetch(domain:sanctionslistservice.ofac.treas.gov)",
      "WebFetch(domain:www.treasury.gov)",
      "WebFetch(domain:ofac.treasury.gov)",
      "WebFetch(domain:api.opensanctions.org)",
      "WebFetch(domain:comtradeapi.un.org)",
      "WebFetch(domain:api.acleddata.com)",
      "WebFetch(domain:api.gdeltproject.org)",
      "WebFetch(domain:sh.dataspace.copernicus.eu)",
      "WebFetch(domain:identity.dataspace.copernicus.eu)",
      "WebFetch(domain:catalogue.dataspace.copernicus.eu)",
      "WebFetch(domain:newsapi.org)",
      "WebFetch(domain:web.archive.org)",
      "WebFetch(domain:archive.org)",
      "WebFetch(domain:httpbin.org)",

      "WebSearch"
    ]
  }
}
```

**Why this list:**

- **Bash is uv-only for Python.** No `python3 *` — that would silently bypass the project's `uv` + `pyproject.toml` convention. If a fetcher tries to run bare `python3`, the hard-fail discipline (see `skills/handling-credentials-safely`) catches it rather than letting it through.
- **WebFetch is per-domain**, never broad. Each entry corresponds to one API the plugin documents. Adding a new fetcher means adding the domain explicitly.
- **WebSearch is broad** — research use needs flexibility, and search results are read-only.
- **No `chmod`, no `python3` fallback, no destructive Bash patterns.** If you need them for one-off setup, run them yourself; they shouldn't be in an always-allow list.

If you skip these allows, Claude Code will prompt per call. That's safe — and you can promote the patterns you trust to allows after a few sessions of seeing what fires.

---

## API keys (in order of likely impact)

`.env.example` ships placeholder slots for every key the plugin understands. Copy to `.env`, then fill in keys top-to-bottom — each tier multiplies what the analyst can verify live.

### Tier 0 — no key needed

These work out of the box:

- **GDELT** (global news at scale, 100+ languages) — used by `fetching-news-gdelt`
- **OFAC SDN raw feeds** — used by `fetching-ofac-sanctions` for the sanctions list itself
- **RSS feeds** — used by `fetching-rss-watchlist` for outlet-level monitoring
- **Wayback Machine** — used by `archiving-with-wayback` for snapshot evidence


### Tier 1 — free, instant, do these first (~10 min total)

These unlock the macro/markets/regulatory backbone:

| Key | Source | Where to register | Why first |
|---|---|---|---|
| **`FRED_API_KEY`** | St Louis Fed (macro time series) | [fred.stlouisfed.org/docs/api/api_key.html](https://fred.stlouisfed.org/docs/api/api_key.html) | Most assessments need at least one macro number. Used by every economic / public-finance lens. |
| **`EIA_API_KEY`** | US Energy Information Admin | [eia.gov/opendata/register.php](https://eia.gov/opendata/register.php) | Oil/gas/power data; cross-checks the energy framing of any geopolitical analysis. |
| **`EDGAR_USER_AGENT`** | SEC EDGAR (US corporate filings) | No registration — set to `"<your-name> <your-email>"` | SEC's terms require a real reachable email. Without it, EDGAR returns 403. |
| **`COMTRADE_KEY`** | UN Comtrade (bilateral merchandise trade) | [comtradeplus.un.org](https://comtradeplus.un.org/api/Subscription) | The "who depends on whom" data layer — supply chains, sanctions effectiveness, BoP composition. |
| **`OPENSANCTIONS_KEY`** | OpenSanctions (cross-list aggregation) | [opensanctions.org/api](https://www.opensanctions.org/api/) | Entity-resolution across 150+ sanctions, PEP, and watchlists with built-in transliteration. |

### Tier 2 — free, useful for specialised topics

| Key | Source | Use |
|---|---|---|
| **`ACLED_KEY` + `ACLED_EMAIL`** | Armed Conflict Location & Event Data | Conflict tempo, named-actor event histories, base rates for political violence |
| **`TELEGRAM_API_ID` + `TELEGRAM_API_HASH`** | [my.telegram.org/apps](https://my.telegram.org/apps) | Authenticated channel history + search. The `t.me/s/<channel>` HTML mirror works without these for read-only browsing — only register when you need history beyond ~20 posts or media download |
| **`SH_CLIENT_ID` + `SH_CLIENT_SECRET`** | Copernicus Data Space Ecosystem | Free Sentinel-1 SAR + Sentinel-2 optical imagery; verification of physical claims |
| **`NEWSAPI_KEY`** | NewsAPI | Current articles; free tier 100/day. GDELT can substitute for most use cases. |
| **`ALPHAVANTAGE_KEY`** | Alpha Vantage | Equities/FX backup when FRED's coverage is thin |
| **`DEEPL_API_KEY`** | DeepL Pro | Foreign-language translation. Pro tier strongly recommended for stakes-grade work. |
| **`ENTSOE_API_KEY`** | ENTSO-E Transparency Platform | European power markets data |
| **`OPENSKY_USER` + `OPENSKY_PASS`** | OpenSky Network | ADS-B aircraft tracking (research-friendly tier) |

### Tier 3 — paid sources (only if you have a subscription)

`.env.example` declares slots for these so the SessionStart hook tracks them, but they're never required. The plugin works without them; they just upgrade specific data layers:

- **Bloomberg** (`BLOOMBERG_TOKEN`) — markets, deep news archive
- **LSEG / Refinitiv** (`LSEG_REFINITIV_APP_KEY`) — Reuters wire archive at source
- **Factiva** (`FACTIVA_USER` + `FACTIVA_PASS`) — historical newspaper depth
- **Janes** (`JANES_TOKEN`) — defence intelligence
- **Kpler** (`KPLER_TOKEN` + `KPLER_USER`) — vessel-level commodity flows
- **Planet** (`PLANET_API_KEY`), **Maxar** (`MAXAR_API_KEY`) — sub-metre satellite imagery
- **Lloyd's List Intelligence** (`LLOYDS_LIST_TOKEN`) — maritime
- **Platts** (`PLATTS_TOKEN`), **Argus** (`ARGUS_TOKEN`) — commodity pricing benchmarks

### What the SessionStart hook tells you

Every Claude Code session in this directory runs `hooks/SessionStart.sh`, which diffs `.env.example` against `.env` and prints a one-line summary:

```
strategic-analyst plugin — credential check
  .env loaded from /path/to/.env
  9 keys set, 16 missing
  dark sources this session: ENTSOE_API_KEY OPENSKY_USER OPENSKY_PASS DEEPL_API_KEY ...
```

The "dark sources" are not errors — they're notice. Skills that need a missing key apply the hard-fail rule (refuse with one line) rather than silently degrading; everything else continues to work.

---

## How to use it

Four user-facing slash commands:

| Command | What it does |
|---|---|
| `/strategic-brief <topic>` | Full deep-brief workflow: provenance → fetch → ledger → lens triage → synthesis → red-team → BLUF document at `briefs/<topic>-<date>.md` plus `evidence/<topic>-<date>.csv` |
| `/daily-sitrep [topic-filter]` | Sweep the configured RSS watchlist, dedupe vs prior runs, cross-reference indicators from open briefs, produce one-screen sitrep at `sitreps/sitrep-<date>.md` |
| `/verify-claim <url-or-claim>` | Single-claim verification with two-source rule, primary fetch, archive, Admiralty grading, ledger row + verdict |
| `/red-team` | Independent stress-test of an existing assessment — KAC, alternative hypotheses, weakest-evidence downgrade, pre-mortem, calibration adjustment |

Or just describe a problem:

> Analyse this Reuters story about Argentina's capital controls. What does it mean and what should we be watching for?

The plugin's skill descriptions should auto-fire the right chain.

### The intended workflow

```
[1] Provenance → [2] Verify → [3] Contextualise → [4] Lens stack
              → [5] Hypotheses → [6] Synthesise → [7] Red-team
```

Documented in detail at [`skills/strategic-news-analysis/SKILL.md`](skills/strategic-news-analysis/SKILL.md). Most events use 2–3 lenses, not all 7 — `synthesising-strategic-assessment` triages.

### What to expect

- Briefs use the **BLUF (Bottom Line Up Front)** format: calibrated probability bands, confidence stated separately, lens ranking, verification gaps explicit, indicators-to-watch with thresholds and time horizons.
- Every load-bearing claim has a row in the evidence ledger with primary URL, Admiralty grades, and accessed-at timestamp.
- The red-team typically moves the calibration by 5–15 percentage points — if it doesn't, the skill flags suspected reasoning-chain contamination.
- If a fetch capability is missing (sandbox blocked, key absent), the slash commands **refuse with one line** rather than producing inference-grade output. This is intentional: a polished hedged brief is worse than no brief.

---

## What's in it

```
strategic-analyst/
├── .claude-plugin/plugin.json
├── .env.example                    # credential template
├── pyproject.toml + uv.lock        # uv-managed Python deps
├── agents/                         # 3 subagent specs
│   ├── lens-applier.md             #   one lens, one finding (parallel-friendly)
│   ├── source-ingestor.md          #   bulk fetch + condense; keeps raw text out of main thread
│   └── red-teamer.md               #   independent review of a finished assessment
├── commands/                       # 4 slash commands (above)
├── config/watchlist.example.yaml   # starter outlets + topic keywords
├── hooks/SessionStart.sh           # credential-check on startup
├── skills/                         # 26 skills total
│   ├── strategic-news-analysis/    #   parent workflow + source hierarchy + data-sources reference
│   ├── analysing-{economic, political, historical, demographic,
│   │                military, public-finance, geographic}-lens/
│   ├── synthesising-strategic-assessment/
│   ├── red-teaming-analysis/
│   ├── building-evidence-ledger/   #   the artefact discipline
│   ├── handling-credentials-safely/  # leak prevention + hard-fail rule
│   ├── searching-web-with-operators/ # Google/Yandex/Bing operators + recipes
│   ├── fetching-news-gdelt/, fetching-rss-watchlist/, fetching-fred-macro/
│   ├── fetching-acled-events/, fetching-comtrade-trade/, fetching-edgar-filings/
│   ├── fetching-ofac-sanctions/, fetching-eia-energy/, fetching-sentinel-imagery/
│   ├── fetching-telegram-channels/
│   ├── archiving-with-wayback/, geolocating-imagery/, translating-foreign-source/
│   └── producing-deep-brief/, producing-daily-sitrep/
└── tests/fixtures/                 # 10 regression baselines from RED/GREEN runs
    ├── live-api-tests-2026-05-05/  #   per-fetcher live tests (FRED, EIA, EDGAR, OFAC, Sentinel)
    ├── tdd-baseline-2026-05-05/    #   integration test (sandbox-blocked, inference-grade)
    └── tdd-baseline-live-2026-05-05/  # integration test (live keys, real verification)
```

---

## Tradecraft references

The skills inherit discipline from the intelligence-community canon:

- ODNI Intelligence Community Directive 203 (analytic standards) and 206 (sourcing).
- *A Tradecraft Primer* (US Government).
- Heuer & Pherson, *Structured Analytic Techniques for Intelligence Analysis*.
- Tetlock, *Superforecasting* (calibration discipline).
- Reinhart & Rogoff, *This Time Is Different* (base rates).
- Heuer, *Psychology of Intelligence Analysis* (1999).

Source-grading uses the **Admiralty system** (A–F for source reliability × 1–6 for information credibility). Calibrated probability bands follow the IC scale (almost no chance / very unlikely / unlikely / roughly even / likely / very likely / almost certainly).

---

## Status

| Component | State |
|---|---|
| Parent + 7 lens skills | Shipped |
| Synthesis + red-team skills | Shipped |
| Evidence-ledger skill | Shipped, TDD-verified |
| Credentials-safety skill | Shipped, validated under the live TDD pass |
| Web-search-with-operators skill | Shipped |
| Fetcher MVP (GDELT, RSS, FRED) | Shipped; gdelt + fred TDD-verified live |
| Tier-2 fetchers (ACLED, Comtrade, EDGAR, OFAC, EIA) | Shipped; EDGAR + OFAC + EIA TDD-verified live |
| Verification helpers (Wayback, Geolocating, Translating) | Shipped; translating TDD-verified |
| Sentinel imagery skill | Shipped, TDD-verified live (CDSE OAuth + STAC + Process API) |
| Telegram channels skill | Shipped (HTML-mirror path needs no auth; authenticated-API path needs `my.telegram.org` registration) |
| Output formats (deep-brief, daily-sitrep) | Shipped; daily-sitrep TDD-verified |
| 4 slash commands | Shipped; `/strategic-brief` and `/daily-sitrep` TDD-verified |
| 3 agent specs | Shipped, all 3 TDD-verified |
| SessionStart credential-check hook | Shipped, working |
| Hard-fail-on-missing-permissions discipline | Propagated across commands + agents + central skill |
| Plugin published to a marketplace | TODO (depends on use case) |

Each skill that ships goes through the writing-skills RED → GREEN → REFACTOR cycle. Test fixtures from GREEN runs live in `tests/fixtures/`. Re-running them after dependency or API changes detects regressions.

---

## Licence

MIT.
