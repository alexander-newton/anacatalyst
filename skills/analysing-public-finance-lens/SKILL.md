---
name: analysing-public-finance-lens
description: Use when an event implicates sovereign finances — budgets, tax changes, debt issuance, IMF programmes, rating actions, or FX-mismatched debt. Triggers include "can they afford this", "is the debt sustainable", "what's the fiscal cost", "default risk", "credit downgrade", or solvency-vs-liquidity calls.
---

# Applying the Public-Finance Lens

## Overview

The public-finance lens reads events as movements of sovereign cash flows, balance-sheet positions, and the political economy of taxation and spending. It overlaps with the economic lens but goes deeper on debt sustainability, fiscal space, and the mechanics of sovereign credit.

**Core principle:** *Solvency is about long-run cash flows; liquidity is about today's payment capacity. Most sovereign crises are liquidity events, not solvency events.* Conflating them produces both false alarms and missed warnings.

## When to Use

- Budget proposals, tax changes, fiscal stimulus or austerity packages.
- Sovereign bond issuances, yield moves, restructurings, defaults.
- Credit-rating actions (Moody's, S&P, Fitch).
- IMF programmes — Article IV consultations, Stand-By Arrangements, EFF, RFI/RCF, debt restructurings.
- Currency-mismatched debt, "original sin" claims.
- Pension or health-system fiscal stress.
- Sanctions affecting a sovereign's payment systems or reserves.

## The Frameworks

### Debt sustainability

The standard sovereign debt accumulation identity (in % of GDP):

```
Δb_t = (r - g) / (1 + g) × b_{t-1} − pb_t + sf_t
```

where `b` = debt/GDP, `r` = effective real interest rate on debt, `g` = real growth rate, `pb` = primary balance/GDP, `sf` = stock-flow adjustment (off-balance-sheet items, valuation effects).

Read this as: **debt rises** if r > g and primary balance is insufficient, OR if there are stock-flow shocks (FX devaluation on foreign-currency debt, recognition of contingent liabilities).

- **The (r − g) term is decisive.** When r < g, debt erodes naturally even with deficits. When r > g, even balanced budgets imply growing debt; primary surpluses are required.
- **Debt-stabilising primary balance:** `pb* = (r − g) / (1 + g) × b`. If actual `pb < pb*`, debt grows.
- **IMF DSA framework** — official toolkit applies stress tests (growth shock, interest-rate shock, exchange-rate shock, contingent-liability shock) to a baseline, classifies debt-distress risk into low/moderate/high/in-distress for low-income countries (LIC-DSF) and produces a heat map for market-access countries (MAC-DSA).

### Solvency vs liquidity

- **Solvency:** present value of future primary surpluses ≥ outstanding debt. Long-horizon question; depends on assumed `r`, `g`, `pb` paths.
- **Liquidity:** can the state make today's payments? Even solvent states can default if creditors won't roll over (rollover risk). This is where most actual crises happen.
- **Self-fulfilling debt crises (Cole-Kehoe):** at intermediate debt levels, multiple equilibria — markets that *believe* default is coming raise yields, making default rational. Central-bank backstops (ECB OMT, IMF programmes) work by ruling out the bad equilibrium.

### Sovereign-credit drivers (as used by rating agencies and analysts)

- **Economic strength** — GDP per capita, growth volatility, diversification.
- **Institutional strength** — fiscal frameworks, central-bank independence, governance.
- **Fiscal strength** — debt/GDP, debt structure (currency, maturity, holders), interest burden, fiscal flexibility (tax base, spending rigidity).
- **Susceptibility to event risk** — political risk, banking-sector risk, external vulnerability, environmental risk.

### "Original sin" and currency mismatch

- Many emerging markets cannot borrow long-term in their own currency; must issue in USD/EUR. Devaluation then balloons local-currency debt service even when trade balance improves.
- **Net foreign-currency position** of the consolidated public sector (including SOEs) is the right unit to watch — assets (reserves, sovereign-wealth funds) net of liabilities (USD bonds, FX-linked debt).

### Fiscal multipliers and constraints

- Multipliers larger in: recessions, monetary accommodation, closed economies, transfer-targeted spending.
- Smaller in: open economies (import leakage), tight monetary policy, near-full-employment, public-debt-stressed states.
- **Crowding out** matters mainly when monetary policy isn't accommodative.
- **Ricardian equivalence** holds at the limit — households save in anticipation of future taxes — but is partial in practice; presence/absence depends on credit constraints and time horizons.

### Tax & spending

- **Tax-to-GDP ratio benchmarks:** OECD average ~33%, US ~28%, Nordics ~42%, EM average ~17%, LICs often <15%. A state with low tax capacity has limited fiscal space regardless of debt level.
- **Spending rigidity** — interest payments, pensions, public-sector wages, mandated transfers. The discretionary share is what's actually available for adjustment.
- **Composition of revenue** — commodity revenue (volatile), VAT (broad-based, regressive), income tax (cyclical), tariffs (trade-war exposed) imply different fiscal vulnerability.

### Sanctions on sovereigns

- **Reserve freezes** convert liquid assets into encumbered ones — affects ability to defend currency and service external debt.
- **Capital-market exclusion** removes refinancing channels; impact depends on time to maturity, share of foreign-held debt, and alternative funding sources (BRICS+, bilateral lines).
- **Payment-system sanctions** (SWIFT removal, OFAC SDN) raise transaction costs and create workarounds (correspondent banking through third parties, alternative messaging).

## Quick Indicators

| Question | Indicator |
|----------|-----------|
| Debt sustainable? | Debt/GDP, effective r, growth, debt-stabilising primary balance, currency composition, maturity profile |
| Liquidity tight? | Gross financing needs (GFN), reserves/short-term debt, recent auction tails, CDS spreads |
| Sovereign credit pressure? | Spread vs benchmark, CDS, rating history and outlook, IMF involvement, Article IV tone |
| Fiscal flexibility? | Tax/GDP, share of mandatory spending, off-budget liabilities, contingent liabilities (banks, SOEs) |
| External vulnerability? | Net IIP, foreign-currency-denominated debt share, FX reserves (months of imports, % of short-term debt) |

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Treating debt/GDP as the threshold | Composition, currency, maturity, holder base matter as much as level |
| Confusing solvency with liquidity | Many "default" stories are rollover failures; the sustainability picture may be fine |
| Static r-g comparisons | r and g can move together; assume joint paths, not independent |
| Ignoring contingent liabilities | Banking-sector recapitalisation can dwarf headline debt |
| One-side-of-balance-sheet thinking | Reserves and SWFs offset external debt; net position is what matters |
| Stock-flow accounting errors | A devaluation on FX debt is a *stock* shock — doesn't show in primary balance |
| Treating IMF programmes as bailouts | Conditionality and reform are the substance; the loan size is often modest relative to GFN |
| Linear extrapolation of bond yields | Self-fulfilling dynamics produce non-linear moves around equilibria |

## Worked Example

*Headline: "Country X downgraded to junk; finance minister says debt sustainable, IMF talks 'precautionary'"* — through the lens:

- **Solvency vs liquidity:** Downgrade most likely captures *liquidity* concerns (rollover, reserves) rather than long-run solvency. Check spread move on different maturity points — front-end blow-out signals liquidity; parallel widening signals solvency.
- **Debt accumulation identity:** Plug current `r`, `g`, `pb`, FX moves into the equation. Is the debt-stabilising primary balance achievable? If `pb*` requires fiscal tightening 3+ pp of GDP from a position the government has already shown it can't deliver, "sustainable" is rhetorical.
- **Currency composition:** What share is FX-denominated? If high and the currency is sliding, the stock-flow term will dwarf the flow.
- **Reserves cover:** Months of imports, reserves vs short-term external debt. Below 3 months / 100% indicates real liquidity strain.
- **IMF as backstop:** "Precautionary" arrangements (PLL, FCL) are credible-reformer signals; "Stand-By" or EFF imply bigger problems. RCF/RFI are smallest, fastest, lowest-conditionality.
- **Indicators to watch:** Auction bid-to-cover at next issuance, CDS curve shape, central-bank FX intervention, IMF mission timing, primary-balance trajectory in the next budget.

## Source Inputs

IMF Article IV reports, IMF DSA tables, IMF Fiscal Monitor, World Bank LIC-DSF, BIS public debt statistics, national debt management offices (DMOs), central banks, OECD Revenue Statistics, ICE/Bloomberg/Refinitiv for sovereign yields and CDS, S&P/Moody's/Fitch sovereign reports. See `data-sources.md` in the parent skill.

## Canonical References

- IMF, *Staff Guidance Note on Public Debt Sustainability Analysis in Market Access Countries*
- IMF/World Bank, *Debt Sustainability Framework for Low-Income Countries*
- Reinhart & Rogoff, *This Time Is Different*
- Bohn (1998) on the fiscal-policy reaction function
- Cole & Kehoe on self-fulfilling debt crises
- Eichengreen, Hausmann & Panizza on "original sin"
