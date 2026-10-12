# DR Congo National OpenSourceRail Strategy

This page contains only DR Congo-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$40.72 B (87.8%) of external capital** and **$52.61 B of external interest**. Capital plus saved interest totals **$93.33 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 7 |
| Represented population | 27,007,000 |
| Trainsets / vehicle modules | 2,678 / 13,835 |
| City infrastructure and fleet CAPEX | $25.00 B |
| Shared national factory | $703.2 M |
| Factory sizing basis | 10,650 modules for Kinshasa, then reused nationally |
| **Total national programme** | **$25.75 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $5.63 B (21.9%) |
| Domestic / local capital | $20.12 B (78.1%) |
| Annual external capital draw | $563.3 M / yr |
| Annual local capital draw | $2.01 B / yr |
| Annual public construction commitment | $2.75 B / yr for 10 years |
| Annual post-grace debt service | $2.49 B / yr |
| Default foreign-turnkey external capital | $46.36 B |
| External capital saved | $40.72 B |
| Capital + lifetime external interest saved | $93.33 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $10.69 B | $1.60 B | $9.08 B |
| Stations | $5.89 B | $1.18 B | $4.71 B |
| Depots | $1.13 B | $281.3 M | $843.8 M |
| Rolling stock | $3.90 B | $1.36 B | $2.53 B |
| Dedicated solar plants | $1.52 B | $682.4 M | $834.1 M |
| Residual train control | $55.9 M | $27.9 M | $27.9 M |
| Charging microgrids | $291.7 M | $116.7 M | $175.0 M |
| EPC / project services | $1.59 B | $237.8 M | $1.35 B |
| Shared national trainset factory | $703.2 M | $140.6 M | $562.6 M |
| **Total** | **$25.75 B** | **$5.63 B** | **$20.12 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital | Lines | Added lines | Original circles | Current circles |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| [Kinshasa](Kinshasa/README.md) | 17,178,000 | 1,775 | $16.87 B | $3.83 B | $13.04 B | 14 | 5 | 51.6% | 54.8% |
| [Lubumbashi](Lubumbashi/README.md) | 2,829,000 | 190 | $2.21 B | $447.4 M | $1.76 B | 8 | 3 | 21.9% | 23.3% |
| [Mbuji Mayi](Mbuji-Mayi/README.md) | 2,500,000 | 165 | $1.93 B | $390.7 M | $1.54 B | 6 | 2 | 47.0% | 37.5% |
| [Kisangani](Kisangani/README.md) | 1,300,000 | 66 | $751.8 M | $152.4 M | $599.4 M | 3 | 1 | 12.8% | 13.7% |
| [Kananga](Kananga/README.md) | 1,200,000 | 55 | $746.3 M | $146.6 M | $599.8 M | 3 | 1 | 14.3% | 16.9% |
| [Bukavu](Bukavu/README.md) | 1,000,000 | 241 | $1.46 B | $301.4 M | $1.15 B | 5 | 2 | 33.3% | 47.1% |
| [Goma](Goma/README.md) | 1,000,000 | 186 | $1.04 B | $218.0 M | $818.7 M | 5 | 2 | 30.2% | 36.5% |

## Local Basis And Regeneration

Country finance parameters use `CD` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
