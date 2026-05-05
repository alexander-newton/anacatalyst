---
name: analysing-economic-lens
description: Use when interpreting currency moves, trade flows, inflation prints, growth data, sanctions, supply-chain shocks, commodity moves, or central-bank actions. Triggers include "what's the economic impact", "why did markets move", "is this inflationary", "who wins from this trade policy", or any claim of economic causation.
---

# Applying the Economic Lens

## Overview

The economic lens reads events as adjustments to relative prices, flows, and constraints. The analyst's job is not to forecast next quarter's GDP — it is to identify which canonical mechanism is operating, and what the second-order effects through prices and flows will be.

**Core principle:** *Every economic event redistributes. Identify the gainers, the losers, and the constraint that's binding.* Headlines describe the event; the framework tells you who pays.

## When to Use

- News mentions GDP, inflation, unemployment, currency, trade balance, capital flows, or commodity prices.
- A policy change has price or quantity effects (tariffs, sanctions, subsidies, rate decisions).
- The story is framed as "X helps the economy" or "Y is bad for growth" — claims that require unpacking.
- A market reacted to news and the user wants to know why.
- An economic claim is being used to justify a non-economic conclusion.

## The Frameworks

### Open-economy macro

- **Mundell-Fleming / Impossible Trinity** — a country can have at most two of: open capital account, fixed exchange rate, independent monetary policy. When a third is attempted, something breaks (capital flight, devaluation, lost monetary control). Use this to read currency crises, capital controls, and central-bank decisions.
- **Balance of payments identity** — current account + capital account = 0 (with reserves and errors). A current-account deficit is *financed*; ask by what (FDI, portfolio inflows, sovereign borrowing, reserves drawdown). The financing mix is the risk story.
- **Real exchange rate** — competitiveness depends on nominal FX × relative prices. A nominal depreciation that's matched by inflation is no real depreciation.
- **Sudden stop** (Calvo) — capital inflows reverse abruptly; current-account adjustment is forced through compression of imports and growth. Watch for: rising EM spreads, falling reserves, IMF inquiries.

### Trade & industrial policy

- **Comparative advantage (Ricardo)** — countries gain from trade by specialising in lowest opportunity-cost goods. Tariffs reduce aggregate welfare but redistribute. Always ask: who is the protected sector, who is the consumer paying.
- **Gravity model** — bilateral trade ≈ f(GDP_i × GDP_j / distance). Use to sanity-check claims that "country X will replace country Y as a supplier" — geography and size constrain plausible reallocation.
- **Stolper-Samuelson / specific factors** — protection raises returns to the scarce factor (often labour in advanced economies). Tells you the political economy: tariffs have winners, who lobby; consumers lose diffusely and don't.
- **Dutch disease / resource curse** — commodity booms appreciate the real exchange rate, hollow out tradable manufacturing, and concentrate fiscal exposure to commodity prices.

### Inflation & monetary

- **Phillips curve, expectations-augmented** — inflation = expectations + output-gap term + supply shocks. Anchored expectations matter more than current slack. Read central-bank statements for *expectations management*, not just rate decisions.
- **Quantity theory at the limit** — sustained high inflation is a monetary/fiscal phenomenon (fiscal dominance), not a transitory shock.
- **Pass-through** — FX and import-price changes pass through to consumer prices with country-specific elasticities. Small open economies see fast, full pass-through.

### Cycles & shocks

- **Output gap, NAIRU** — distinguish cyclical from structural. A recession that closes a positive output gap is different from one driven by supply destruction.
- **Multiplier** — fiscal multipliers are larger at the zero lower bound, in recessions, and for spending vs tax cuts; smaller in open economies (leakage to imports).
- **Financial accelerator (Bernanke)** — balance-sheet effects amplify shocks. Watch for: leverage build-ups, currency mismatches, asset-price collapses.

### Sanctions & coercion

- **Sanctions effectiveness** depends on: target's substitutability of inputs/outputs, multilateral coverage, time horizon, and whether the regime can shift costs to the population. Sanctions usually fail at regime change and succeed at constraint.
- **Secondary sanctions and dollar dominance** — extraterritorial reach derives from USD clearing through US banks; counter-strategies (CIPS, mBridge) are slow.

## Quick Indicators Reference

| Question | Indicator |
|----------|-----------|
| Currency under pressure? | NEER/REER vs trend, FX reserves trajectory, NDF spreads, sovereign CDS |
| Inflation persistent? | Core inflation, services inflation, expectations (surveys, breakevens), unit labour costs |
| Recession risk? | Yield-curve spreads (10y-3m, 10y-2y), PMI new orders, claims, credit spreads |
| Trade integration? | Trade/GDP, intra-industry trade index, supplier concentration |
| External vulnerability? | CA balance/GDP, short-term external debt/reserves, reserve cover (months of imports) |

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Treating GDP growth as welfare | Composition matters; commodity-driven growth ≠ broad-based |
| Confusing nominal with real | Always check whether numbers are inflation-adjusted, FX-adjusted |
| Headline trade balance fixation | Bilateral balances mean little; look at multilateral position |
| "Sanctions hurt the economy" without specificity | Which sector, which input, what's the substitution path |
| One-period thinking | Adjustment happens; ask what equilibrium the system is moving to |
| Ignoring expectations | A central-bank tone shift matters more than the rate decision itself |
| Mistaking correlation for transmission | Commodity prices and EM currencies move together; that doesn't mean one *causes* the other in this episode |

## Worked Example

*"Country X imposes 25% tariff on imported steel"* — through the lens:

- **Comparative advantage:** Aggregate welfare loss; the protected sector gains, downstream users (autos, construction) and consumers lose.
- **Stolper-Samuelson:** Steelworkers gain; the loss is dispersed across millions of consumers — explains why this is politically attractive despite being negative-sum.
- **Pass-through:** Steel-using prices rise; magnitude depends on tradability of downstream goods (cars yes, buildings less).
- **Gravity:** Imports don't disappear, they reroute; check transhipment via lower-tariff jurisdictions.
- **Retaliation expected:** Identify exporters to country X with political weight in retaliating economies (agricultural goods commonly chosen — concentrated, photogenic, politically sensitive).
- **Indicator to watch:** Steel input prices in downstream sectors at 3- and 6-month horizon; auto-sector margins; trade complaints filed at WTO.

## Source Inputs

For data on this lens, see `data-sources.md` in the parent skill: IMF WEO/IFS/BoP, World Bank WDI, OECD, FRED, BIS, Eurostat, national statistical offices, UN Comtrade. **For sovereign-debt and fiscal-specific analysis** that goes deeper than this skill, use the public-finance lens skill — they overlap but the public-finance lens has richer treatment of debt sustainability mechanics.

## Canonical References

- Krugman, Obstfeld & Melitz, *International Economics* (textbook)
- Blanchard, *Macroeconomics* (textbook)
- Reinhart & Rogoff, *This Time Is Different* (financial-crisis history)
- Mundell (1963), Fleming (1962) on trilemma
- Calvo (1998) on sudden stops
