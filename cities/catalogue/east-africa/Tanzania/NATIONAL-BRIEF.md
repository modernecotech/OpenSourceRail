# Tanzania National OpenSourceRail Strategy

This page contains only Tanzania-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$41.29 B (88.3%) of external capital** and **$51.76 B of external interest**. Capital plus saved interest totals **$93.05 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 15 |
| Represented population | 13,854,689 |
| Trainsets / vehicle modules | 2,918 / 11,768 |
| City infrastructure and fleet CAPEX | $25.00 B |
| Shared national factory | $910.8 M |
| Factory sizing basis | 6,318 modules for Dar Es Salaam, then reused nationally |
| **Total national programme** | **$25.98 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $5.47 B (21.1%) |
| Domestic / local capital | $20.51 B (78.9%) |
| Annual external capital draw | $781.6 M / yr |
| Annual local capital draw | $2.93 B / yr |
| Annual public construction commitment | $2.39 B / yr for 7 years |
| Annual post-grace debt service | $1.96 B / yr |
| Default foreign-turnkey external capital | $46.76 B |
| External capital saved | $41.29 B |
| Capital + lifetime external interest saved | $93.05 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $12.78 B | $1.92 B | $10.87 B |
| Stations | $4.18 B | $836.2 M | $3.34 B |
| Depots | $1.44 B | $361.1 M | $1.08 B |
| Rolling stock | $3.36 B | $1.18 B | $2.19 B |
| Dedicated solar plants | $1.46 B | $655.6 M | $801.3 M |
| Residual train control | $67.4 M | $33.7 M | $33.7 M |
| Charging microgrids | $168.9 M | $67.6 M | $101.4 M |
| EPC / project services | $1.60 B | $240.6 M | $1.36 B |
| Shared national trainset factory | $910.8 M | $182.2 M | $728.6 M |
| **Total** | **$25.98 B** | **$5.47 B** | **$20.51 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital | Lines | Added lines | Original circles | Current circles |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| [Dar Es Salaam](Dar-Es-Salaam/README.md) | 7,404,689 | 1,053 | $12.15 B | $2.69 B | $9.46 B | 14 | 5 | 44.3% | 45.5% |
| [Mwanza](Mwanza/README.md) | 1,100,000 | 298 | $3.44 B | $700.5 M | $2.74 B | 9 | 3 | 50.2% | 43.9% |
| [Dodoma](Dodoma/README.md) | 800,000 | 182 | $1.00 B | $205.4 M | $795.9 M | 5 | 2 | 32.4% | 36.8% |
| [Arusha](Arusha/README.md) | 700,000 | 218 | $1.18 B | $242.0 M | $936.0 M | 4 | 1 | 33.7% | 37.0% |
| [Mbeya](Mbeya/README.md) | 550,000 | 182 | $983.0 M | $202.8 M | $780.1 M | 5 | 2 | 37.4% | 37.3% |
| [Morogoro](Morogoro/README.md) | 500,000 | 178 | $1.05 B | $216.7 M | $831.2 M | 5 | 2 | 30.7% | 36.1% |
| [Zanzibar City](Zanzibar-City/README.md) | 500,000 | 186 | $1.04 B | $218.1 M | $819.4 M | 5 | 2 | 40.2% | 37.7% |
| [Tanga](Tanga/README.md) | 400,000 | 178 | $1.02 B | $213.8 M | $808.6 M | 5 | 2 | 29.3% | 48.7% |
| [Kigoma](Kigoma/README.md) | 300,000 | 75 | $522.2 M | $99.4 M | $422.8 M | 4 | 1 | 44.4% | 45.4% |
| [Moshi](Moshi/README.md) | 300,000 | 79 | $623.8 M | $116.0 M | $507.8 M | 4 | 1 | 28.8% | 38.9% |
| [Tabora](Tabora/README.md) | 300,000 | 65 | $458.3 M | $87.5 M | $370.8 M | 4 | 1 | 38.4% | 48.5% |
| [Iringa](Iringa/README.md) | 250,000 | 86 | $622.3 M | $118.3 M | $503.9 M | 4 | 1 | 51.2% | 49.9% |
| [Shinyanga](Shinyanga/README.md) | 250,000 | 77 | $512.3 M | $95.5 M | $416.8 M | 4 | 1 | 38.9% | 43.5% |
| [Songea](Songea/README.md) | 250,000 | 29 | $184.7 M | $35.3 M | $149.4 M | 2 | 0 | 24.3% | 24.3% |
| [Sumbawanga](Sumbawanga/README.md) | 250,000 | 32 | $219.0 M | $42.9 M | $176.1 M | 3 | 0 | 42.4% | 42.4% |

## Local Basis And Regeneration

Country finance parameters use `TZ` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
