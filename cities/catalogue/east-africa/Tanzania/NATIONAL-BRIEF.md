# Tanzania National OpenSourceRail Strategy

This page contains only Tanzania-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$57.96 B (88.1%) of external capital** and **$72.65 B of external interest**. Capital plus saved interest totals **$130.61 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 15 |
| Represented population | 13,854,689 |
| Trainsets / vehicle modules | 4,667 / 18,579 |
| City infrastructure and fleet CAPEX | $35.60 B |
| Shared national factory | $869.8 M |
| Factory sizing basis | 9,492 modules for Dar Es Salaam, then reused nationally |
| **Total national programme** | **$36.53 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $7.79 B (21.3%) |
| Domestic / local capital | $28.73 B (78.7%) |
| Annual external capital draw | $1.11 B / yr |
| Annual local capital draw | $4.10 B / yr |
| Annual public construction commitment | $3.36 B / yr for 7 years |
| Annual post-grace debt service | $2.76 B / yr |
| Default foreign-turnkey external capital | $65.75 B |
| External capital saved | $57.96 B |
| Capital + lifetime external interest saved | $130.61 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $16.12 B | $2.42 B | $13.70 B |
| Stations | $7.11 B | $1.42 B | $5.69 B |
| Depots | $2.94 B | $734.7 M | $2.20 B |
| Rolling stock | $5.31 B | $1.86 B | $3.45 B |
| Dedicated solar plants | $1.53 B | $687.6 M | $840.4 M |
| Residual train control | $86.5 M | $43.2 M | $43.2 M |
| Charging microgrids | $276.8 M | $110.7 M | $166.1 M |
| EPC / project services | $2.29 B | $343.4 M | $1.95 B |
| Shared national trainset factory | $869.8 M | $174.0 M | $695.8 M |
| **Total** | **$36.53 B** | **$7.79 B** | **$28.73 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Dar Es Salaam](Dar-Es-Salaam/README.md) | 7,404,689 | 1,582 | $15.34 B | $3.48 B | $11.86 B |
| [Mwanza](Mwanza/README.md) | 1,100,000 | 595 | $5.24 B | $1.11 B | $4.13 B |
| [Dodoma](Dodoma/README.md) | 800,000 | 314 | $1.79 B | $364.2 M | $1.42 B |
| [Arusha](Arusha/README.md) | 700,000 | 390 | $2.14 B | $440.9 M | $1.70 B |
| [Mbeya](Mbeya/README.md) | 550,000 | 292 | $1.62 B | $334.4 M | $1.29 B |
| [Morogoro](Morogoro/README.md) | 500,000 | 308 | $1.83 B | $377.4 M | $1.45 B |
| [Zanzibar City](Zanzibar-City/README.md) | 500,000 | 225 | $1.24 B | $260.5 M | $977.3 M |
| [Tanga](Tanga/README.md) | 400,000 | 198 | $1.16 B | $240.9 M | $918.4 M |
| [Kigoma](Kigoma/README.md) | 300,000 | 124 | $852.1 M | $163.6 M | $688.5 M |
| [Moshi](Moshi/README.md) | 300,000 | 148 | $1.06 B | $199.9 M | $855.6 M |
| [Tabora](Tabora/README.md) | 300,000 | 94 | $606.0 M | $117.3 M | $488.7 M |
| [Iringa](Iringa/README.md) | 250,000 | 112 | $811.7 M | $154.6 M | $657.0 M |
| [Shinyanga](Shinyanga/README.md) | 250,000 | 147 | $1.01 B | $192.4 M | $821.2 M |
| [Songea](Songea/README.md) | 250,000 | 68 | $450.1 M | $87.6 M | $362.4 M |
| [Sumbawanga](Sumbawanga/README.md) | 250,000 | 70 | $453.8 M | $89.6 M | $364.2 M |

## Local Basis And Regeneration

Country finance parameters use `TZ` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

| City | Current lines | Added residential lines | Original station circles | Current station circles |
| --- | ---: | ---: | ---: | ---: |
| [Arusha](Arusha/README.md) | 18 | 15 | 33.7% | 72.4% |
| [Dar Es Salaam](Dar-Es-Salaam/README.md) | 38 | 29 | 44.3% | 80.6% |
| [Dodoma](Dodoma/README.md) | 14 | 11 | 32.4% | 73.7% |
| [Iringa](Iringa/README.md) | 7 | 4 | 51.2% | 77.3% |
| [Kigoma](Kigoma/README.md) | 7 | 4 | 44.4% | 79.1% |
| [Mbeya](Mbeya/README.md) | 12 | 9 | 37.4% | 78.3% |
| [Morogoro](Morogoro/README.md) | 12 | 9 | 30.7% | 71.2% |
| [Moshi](Moshi/README.md) | 9 | 6 | 28.8% | 65.4% |
| [Mwanza](Mwanza/README.md) | 20 | 14 | 50.2% | 82.1% |
| [Shinyanga](Shinyanga/README.md) | 9 | 6 | 38.9% | 74.7% |
| [Songea](Songea/README.md) | 5 | 3 | 24.3% | 66.9% |
| [Sumbawanga](Sumbawanga/README.md) | 6 | 3 | 42.4% | 67.2% |
| [Tabora](Tabora/README.md) | 6 | 3 | 38.4% | 74.7% |
| [Tanga](Tanga/README.md) | 7 | 4 | 29.3% | 78.0% |
| [Zanzibar City](Zanzibar-City/README.md) | 9 | 6 | 40.2% | 79.5% |

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
