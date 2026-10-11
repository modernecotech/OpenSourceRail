# DR Congo National OpenSourceRail Strategy

This page contains only DR Congo-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$50.02 B (87.8%) of external capital** and **$64.62 B of external interest**. Capital plus saved interest totals **$114.64 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 7 |
| Represented population | 27,007,000 |
| Trainsets / vehicle modules | 3,625 / 17,523 |
| City infrastructure and fleet CAPEX | $30.72 B |
| Shared national factory | $868.2 M |
| Factory sizing basis | 10,998 modules for Kinshasa, then reused nationally |
| **Total national programme** | **$31.65 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $6.94 B (21.9%) |
| Domestic / local capital | $24.71 B (78.1%) |
| Annual external capital draw | $693.7 M / yr |
| Annual local capital draw | $2.47 B / yr |
| Annual public construction commitment | $3.38 B / yr for 10 years |
| Annual post-grace debt service | $3.06 B / yr |
| Default foreign-turnkey external capital | $56.96 B |
| External capital saved | $50.02 B |
| Capital + lifetime external interest saved | $114.64 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $12.29 B | $1.84 B | $10.44 B |
| Stations | $7.60 B | $1.52 B | $6.08 B |
| Depots | $2.00 B | $498.8 M | $1.50 B |
| Rolling stock | $4.95 B | $1.73 B | $3.21 B |
| Dedicated solar plants | $1.54 B | $692.1 M | $845.9 M |
| Residual train control | $67.2 M | $33.6 M | $33.6 M |
| Charging microgrids | $374.6 M | $149.8 M | $224.8 M |
| EPC / project services | $1.97 B | $295.4 M | $1.67 B |
| Shared national trainset factory | $868.2 M | $173.6 M | $694.6 M |
| **Total** | **$31.65 B** | **$6.94 B** | **$24.71 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Kinshasa](Kinshasa/README.md) | 17,178,000 | 1,833 | $16.79 B | $3.85 B | $12.94 B |
| [Lubumbashi](Lubumbashi/README.md) | 2,829,000 | 508 | $4.50 B | $936.0 M | $3.56 B |
| [Mbuji Mayi](Mbuji-Mayi/README.md) | 2,500,000 | 280 | $2.67 B | $553.0 M | $2.12 B |
| [Kisangani](Kisangani/README.md) | 1,300,000 | 212 | $1.86 B | $388.8 M | $1.47 B |
| [Kananga](Kananga/README.md) | 1,200,000 | 149 | $1.42 B | $290.4 M | $1.13 B |
| [Bukavu](Bukavu/README.md) | 1,000,000 | 307 | $1.67 B | $351.9 M | $1.32 B |
| [Goma](Goma/README.md) | 1,000,000 | 336 | $1.81 B | $382.4 M | $1.42 B |

## Local Basis And Regeneration

Country finance parameters use `CD` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

| City | Current lines | Added residential lines | Original station circles | Current station circles |
| --- | ---: | ---: | ---: | ---: |
| [Bukavu](Bukavu/README.md) | 9 | 6 | 33.3% | 79.3% |
| [Goma](Goma/README.md) | 14 | 11 | 30.2% | 71.4% |
| [Kananga](Kananga/README.md) | 10 | 8 | 14.3% | 34.3% |
| [Kinshasa](Kinshasa/README.md) | 20 | 11 | 51.6% | 80.3% |
| [Kisangani](Kisangani/README.md) | 9 | 7 | 12.8% | 37.4% |
| [Lubumbashi](Lubumbashi/README.md) | 30 | 25 | 21.9% | 55.3% |
| [Mbuji Mayi](Mbuji-Mayi/README.md) | 12 | 8 | 47.0% | 78.7% |

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
