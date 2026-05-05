# Strategic Analyst Data Sources

A working catalogue of authoritative primary and high-quality secondary sources, organised by domain. Use these in preference to general web search when a relevant database exists. APIs and Python clients are noted where available.

This is reference material — read the section relevant to the task at hand rather than the whole file.

---

## Macro & Economic Data

### Global / multilateral

- **IMF Data** (`data.imf.org`, SDMX API) — World Economic Outlook, International Financial Statistics, Balance of Payments, Government Finance Statistics, Direction of Trade Statistics, Article IV reports, Financial Soundness Indicators. The single most useful starting point for cross-country macro.
- **World Bank Open Data** — World Development Indicators (WDI), Global Economic Prospects, debt statistics, Doing Business archive. Python: `wbdata`, `pandas_datareader.wb`.
- **OECD Data Explorer** — STAN industrial database, national accounts, productivity, tax administration comparative data, institutional investor statistics.
- **BIS** (Bank for International Settlements) — international banking statistics, debt securities, FX turnover (triennial), credit-to-GDP gaps.
- **UN DESA / UN Data** — composite portal across 60+ databases.
- **CEPII** — BACI (bilateral trade), CHELEM, gravity datasets.

### National statistical offices (the primary sources)

When a number is reported, find it here first:

- **United States:** BLS (employment, CPI), BEA (GDP, trade), Census, Treasury (TIC, debt, fiscal), Federal Reserve (Z.1 flow of funds, H.4.1, H.6, H.8).
- **United Kingdom:** ONS, HM Treasury, Bank of England, OBR, HMRC.
- **Eurozone:** Eurostat, ECB Statistical Data Warehouse, national statistical offices (Destatis, Insee, Istat, INE).
- **China:** NBS (National Bureau of Statistics), PBoC, SAFE, customs administration, MOFCOM. CEIC for compiled access.
- **Japan:** Statistics Bureau, BoJ, MoF.
- **India:** MOSPI, RBI, CMIE.
- **Brazil:** IBGE, BCB.
- **Russia:** Rosstat, CBR (read with awareness that some series have been restricted/altered post-2022).

### Financial markets / company data

- **FRED** (St. Louis Fed) — vast aggregator of macro and financial time series. Free, API, `pandas_datareader.data.DataReader(..., 'fred')`.
- **SEC EDGAR** — US company filings (10-K, 10-Q, 8-K, 13F). Python: `sec-edgar-downloader`, `edgartools`.
- **Companies House** (UK), **INPI** (France), **Handelsregister** (Germany) — corporate registries.
- **OpenCorporates** — aggregated global corporate data.
- **Bloomberg, Refinitiv (LSEG), FactSet, S&P Capital IQ** — paid; the institutional standard.
- **Yahoo Finance**, **Stooq** — free, lower fidelity. Python: `yfinance`, `pandas_datareader.stooq`.

---

## Trade & Tariffs

- **UN Comtrade** — bilateral merchandise trade by HS code, monthly/annual. Python: `comtradeapicall`. Premium gives bulk download.
- **WTO Stats Portal** — tariff schedules, services trade, dispute settlement.
- **WITS** (World Bank) — combines Comtrade with tariff data (TRAINS).
- **Eurostat Comext** — EU detailed trade statistics.
- **US ITC DataWeb** — US trade data with tariff lookup.
- **CEPII BACI** — reconciled bilateral trade for academic-grade analysis.

---

## Sanctions, Sanctions-Adjacent, and Regulatory Lists

- **OFAC SDN List** (US Treasury) — XML/JSON feed updated as published. Also Sectoral Sanctions Identifications (SSI), Non-SDN lists.
- **EU Consolidated List** of persons, groups and entities subject to EU financial sanctions — XML feed.
- **UK OFSI** consolidated list of financial sanctions targets.
- **UN Security Council Consolidated List**.
- **OpenSanctions** — aggregated, deduplicated, with API. Excellent for entity resolution.
- **Bureau of Industry and Security (BIS)** — Entity List, Unverified List, Military End User List.
- **FinCEN** — beneficial ownership filings (US Corporate Transparency Act, with current scope variations).

---

## Energy

- **EIA** (US Energy Information Administration) — production, consumption, prices, inventories. API and Python: `eia-python`.
- **IEA** — World Energy Outlook, monthly oil data, electricity tracker. Some data paywalled.
- **OPEC Monthly Oil Market Report** — production, demand forecasts, secondary-source production data.
- **JODI** — Joint Organisations Data Initiative, oil and gas, government-reported.
- **Platts / Argus / ICIS** — commodity pricing benchmarks (paywalled, but the prices everyone references).
- **Kpler, Vortexa** — vessel tracking and commodity flows (paid).
- **ENTSO-E Transparency Platform** — European electricity data, free with registration.

---

## Conflict, Security, and Defence

- **SIPRI** — military expenditure, arms transfers, peace operations databases.
- **IISS Military Balance** (annual) — order-of-battle reference (paywalled for current edition).
- **Janes** — defence intelligence, equipment, OOB (paid, professional standard).
- **ACLED** (Armed Conflict Location & Event Data) — coded conflict events, daily updates, API.
- **UCDP** (Uppsala Conflict Data Program) — battle deaths, conflict episodes, organised violence.
- **GTD** (Global Terrorism Database) — events 1970–2020 (note: updates have lagged).
- **NATO public data**, national MoD reports, GAO/CRS/CBO US reports for budget detail.
- **ISW** (Institute for the Study of War) — daily updates on active conflicts; methodology transparent.
- **Bellingcat** — open-source investigations; methodology published per investigation.

---

## Demographics & Social

- **UN World Population Prospects** — biennial, the standard reference.
- **National census offices** — most granular within-country data.
- **DHS Program** — Demographic and Health Surveys, low- and middle-income countries.
- **IPUMS** — harmonised census microdata.
- **OECD Migration Outlook**, **UNHCR Refugee Statistics**, **IOM Migration Data Portal**.
- **Pew Research, Gallup World Poll, V-Dem, World Values Survey** — attitudes, governance.
- **World Bank Worldwide Governance Indicators**.

---

## Geography, Climate, and Environment

- **Natural Earth** — public-domain map data. Python: `cartopy`, `geopandas`.
- **OpenStreetMap** — via Overpass API; Bellingcat's OSM tool for feature-based searches.
- **Copernicus / Sentinel Hub** — free satellite imagery (Sentinel-1 SAR, Sentinel-2 optical).
- **Planet, Maxar, Airbus** — commercial sub-metre imagery (paid).
- **NASA EOSDIS / Worldview** — multi-sensor satellite data.
- **NOAA, ECMWF (Copernicus C3S)** — weather, climate reanalysis.
- **EM-DAT** — international disasters database.
- **Global Forest Watch**, **Global Fishing Watch** — activity tracking with APIs.

---

## Maritime, Aviation, and Logistics

- **AIS / MarineTraffic, VesselFinder** — ship tracking. Raw AIS via providers like Spire, exactEarth.
- **Equasis** — vessel ownership and history (free, reliable).
- **IMO GISIS** — official IMO databases.
- **Lloyd's List Intelligence** — gold-standard maritime, paid.
- **Flightradar24, ADS-B Exchange** — aircraft tracking (ADS-B Exchange is unfiltered).
- **OpenSky Network** — research-friendly ADS-B archive.
- **Eurocontrol, FAA** — flight movement data, NOTAMs.
- **Drewry, Xeneta** — container freight rates.

---

## Government Documents & Legal

- **Federal Register, Congressional Record, GovInfo, Regulations.gov** (US).
- **EUR-Lex** — EU legislation.
- **PACER** (US federal court records, some fees), **CourtListener** (free aggregator).
- **UK Hansard, EU Parliament records, Bundestag DIP, Assemblée nationale**.
- **Foreign Relations of the United States (FRUS)** — declassified diplomatic record.
- **Wilson Center Digital Archive, National Security Archive (GWU)** — declassified documents, multi-country.
- **Freedom of Information Archive (Columbia)** — 4.6M+ declassified docs.
- **Official Gazettes** — most countries publish laws and regulations daily; the actual primary source.

---

## News Collection at Scale

- **GDELT 2.0** — global news monitor in 100+ languages, themes, tone, entities. Python: `gdeltdoc` for the Doc API, `gdelt`/`gdelt-py` for raw events. Caveats: includes lower-quality sources; deduplicate and root-URL-check.
- **Common Crawl** — petabyte web crawl; useful for historical site captures.
- **Internet Archive Wayback Machine** — content provenance (when did a page first appear, when was it changed, when was it deleted). Python: `waybackpy`.
- **Media Cloud** — open-source news analytics platform.
- **NewsAPI / Bing News Search / Google News RSS** — current articles, with usage limits.
- **Factiva, LexisNexis** — paid, archive depth.
- **RSS feeds direct from outlets** — `feedparser`. Cheapest reliable way to track named outlets.

### Translated sources

When the story is in a language you don't read, the translation is part of the analytical question. Useful sources:

- **BBC Monitoring** (paywalled) — translation and analysis of foreign-language broadcasts.
- **MEMRI** (note ideological orientation when reading), **OE Watch** (US Army FMSO).
- Native machine translation (DeepL, Google) is acceptable for screening; for stakes-grade analysis, find an outlet that translated and check the original.

---

## Verification Tools

- **Reverse image search:** Google Images, TinEye, Yandex (often best for non-Western sources).
- **Geolocation:** Google Earth, Yandex Maps, Bellingcat OSM Search, SunCalc (sun-position verification), Mapillary, Wikimapia.
- **EXIF inspection:** `exiftool` (most images stripped on social media; still try).
- **Wayback Machine** for "what did this page say last week / last year".
- **Whois, certificate transparency logs** for site provenance: `crt.sh`, `whoisxmlapi`.

---

## Country Risk and Political Risk Indices

Use these as rough cross-country comparators, not as truth:

- **EIU Country Risk** (paid).
- **PRS Group ICRG** (paid, methodology disclosed).
- **World Bank Worldwide Governance Indicators** (free).
- **Transparency International CPI** — corruption perceptions.
- **Freedom House, V-Dem** — democracy, civil liberties.
- **Fragile States Index** (Fund for Peace).

These indices are inputs, not conclusions. They embed the index-builder's assumptions and lag reality.

---

## Quick Python Snippets

### GDELT — what's the global volume of coverage on a topic, by source country?

```python
from gdeltdoc import GdeltDoc, Filters
gd = GdeltDoc()
f = Filters(keyword="semiconductor export controls",
            start_date="2024-01-01", end_date="2024-12-31")
articles = gd.article_search(f)        # DataFrame of articles
volume = gd.timeline_search("timelinevol", f)
by_country = gd.timeline_search("timelinesourcecountry", f)
```

### World Bank — pull a structural indicator across countries

```python
import wbdata, pandas as pd
# General government gross debt (% of GDP) for selected countries, 2010-2023
data = wbdata.get_dataframe(
    {"GC.DOD.TOTL.GD.ZS": "gov_debt_pct_gdp"},
    country=["TUR", "BRA", "ARG", "EGY", "ZAF"],
)
```

### FRED — recent inflation and policy rate

```python
from pandas_datareader import data as pdr
import datetime as dt
cpi = pdr.DataReader("CPIAUCSL", "fred", dt.date(2015,1,1))   # US CPI
ffr = pdr.DataReader("DFEDTARU", "fred", dt.date(2015,1,1))   # Fed funds upper
```

### OFAC SDN — load and search the sanctions list

```python
import pandas as pd
sdn = pd.read_csv("https://www.treasury.gov/ofac/downloads/sdn.csv",
                  header=None, names=["ent_num","name","sdn_type",
                                       "program","title","call_sign","vess_type",
                                       "tonnage","grt","vess_flag","vess_owner","remarks"])
hits = sdn[sdn["name"].str.contains("ROSNEFT", case=False, na=False)]
```

### ACLED — recent events in a country (requires free API key)

```python
import httpx
r = httpx.get("https://api.acleddata.com/acled/read",
              params={"key": "YOUR_KEY", "email": "you@example.com",
                      "country": "Sudan", "limit": 500})
events = r.json()["data"]
```

### Wayback — when did this page first appear; what did it say earlier?

```python
import httpx
r = httpx.get("http://archive.org/wayback/available",
              params={"url": "example.gov.tr/announcement", "timestamp": "20230101"})
print(r.json())   # nearest snapshot URL and timestamp
```

---

## Notes on Paid Tools

A working strategic analyst typically has access to *some* paid data — Bloomberg, Refinitiv, Janes, Lloyd's List, S&P Platts. When working without them, openly note the gap rather than papering over it: "this analysis would be improved by access to vessel-level AIS history" is more useful than confidently inferring from a screenshot.

The free public sources above cover most analytical needs for most questions. The paid sources matter most for: real-time market data, global vessel/aircraft history beyond a few weeks, defence equipment specifics, and depth of historical news archive.
