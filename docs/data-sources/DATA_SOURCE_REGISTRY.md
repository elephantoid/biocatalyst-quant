# Data Source Registry — candidate versus verified

| Domain | Primary source | Secondary / candidates | Stage | Critical qualification |
|---|---|---|---|---|
| Trials | ClinicalTrials.gov official API, record history | IR/conference | Core source, adapter unverified | historical versions, posted-vs-submitted |
| Drug regulatory | FDA / Drugs@FDA / openFDA | FDA calendars, IR | Core source, adapter unverified | first public release and historical semantics |
| Filings & financials | SEC EDGAR submissions/XBRL | company IR | Core source, adapter unverified | accepted/published time, corrections |
| Announcements | company IR; GlobeNewswire | Business Wire, PR Newswire | First qualification batch | first publication, RSS rights and archive |
| Conferences | ASCO, AACR | ESMO, ASH, AHA | Phase-2 qualification | abstracts/embargo and historic publication times |
| Industry news | Fierce Biotech, STAT, Endpoints, BioPharma Dive | other publishers | Discovery/corroboration only initially | paywalls, access rights, originality and coverage |
| Catalyst calendars | BioPharmCatalyst, BioCatalystWatch | other calendars | Discovery candidates | verify against primary dated evidence |
| Historical news | GDELT | provider archives | Experimental | not first-publication truth; coverage bias |
| Intraday extended hours | Massive (ex Polygon) | Alpaca, Databento | **Unverified candidate** | 5m historical scope, delisted tickers, feeds, cost, license |
| Prototyping prices | Yahoo Finance | — | Exploratory only | intraday limits, survivorship, adjustments |
| Security master/corporate actions | Nasdaq historical products, Sharadar | CRSP if access | **Unverified paid candidates** | listings, identifier reuse, delisting returns, action payouts |
| Macro/benchmarks | FRED; ETF price provider | other feeds | Core research candidate | vintages and historical availability |

Do not assume candidate sources provide full 2015–2026 extended-hours 5-minute and delisted security coverage. Vendor pricing changes; request current written details. Respect terms, rate limits, storage and derived-use permissions.
