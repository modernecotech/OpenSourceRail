# Guinea National OpenSourceRail Strategy

This page contains only Guinea-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$3.57 B (90.0%) of external capital** and **$4.61 B of external interest**. Capital plus saved interest totals **$8.17 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 2,010,000 |
| Trainsets / vehicle modules | 82 / 328 |
| City infrastructure and fleet CAPEX | $1.87 B |
| Shared national factory | $306.6 M |
| Factory sizing basis | 328 modules for Conakry, then reused nationally |
| **Total national programme** | **$2.20 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $397.3 M (18.0%) |
| Domestic / local capital | $1.81 B (82.0%) |
| Annual external capital draw | $39.7 M / yr |
| Annual local capital draw | $180.5 M / yr |
| Annual public construction commitment | $198.4 M / yr for 10 years |
| Annual post-grace debt service | $177.6 M / yr |
| Default foreign-turnkey external capital | $3.96 B |
| External capital saved | $3.57 B |
| Capital + lifetime external interest saved | $8.17 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $1.46 B | $219.5 M | $1.24 B |
| Stations | $68.5 M | $13.7 M | $54.8 M |
| Depots | $50.1 M | $12.5 M | $37.5 M |
| Rolling stock | $91.8 M | $32.1 M | $59.7 M |
| Dedicated solar plants | $72.5 M | $32.6 M | $39.9 M |
| Residual train control | $3.8 M | $1.9 M | $1.9 M |
| Charging microgrids | $6.8 M | $2.7 M | $4.0 M |
| EPC / project services | $139.3 M | $20.9 M | $118.4 M |
| Shared national trainset factory | $306.6 M | $61.3 M | $245.3 M |
| **Total** | **$2.20 B** | **$397.3 M** | **$1.81 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Conakry](Conakry/README.md) | 2,010,000 | 82 | $1.87 B | $332.7 M | $1.54 B |

## Local Basis And Regeneration

Country finance parameters use `GN` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
