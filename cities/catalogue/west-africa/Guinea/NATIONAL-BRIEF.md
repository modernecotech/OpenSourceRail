# Guinea National OpenSourceRail Strategy

This page contains only Guinea-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$2.38 B (88.9%) of external capital** and **$3.07 B of external interest**. Capital plus saved interest totals **$5.45 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 2,010,000 |
| Trainsets / vehicle modules | 87 / 348 |
| City infrastructure and fleet CAPEX | $1.14 B |
| Shared national factory | $321.0 M |
| Factory sizing basis | 348 modules for Conakry, then reused nationally |
| **Total national programme** | **$1.48 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $296.3 M (20.0%) |
| Domestic / local capital | $1.19 B (80.0%) |
| Annual external capital draw | $29.6 M / yr |
| Annual local capital draw | $118.8 M / yr |
| Annual public construction commitment | $132.2 M / yr for 10 years |
| Annual post-grace debt service | $119.0 M / yr |
| Default foreign-turnkey external capital | $2.67 B |
| External capital saved | $2.38 B |
| Capital + lifetime external interest saved | $5.45 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $706.6 M | $106.0 M | $600.6 M |
| Stations | $126.1 M | $25.2 M | $100.9 M |
| Depots | $52.3 M | $13.1 M | $39.2 M |
| Rolling stock | $97.4 M | $34.1 M | $63.3 M |
| Dedicated solar plants | $76.5 M | $34.4 M | $42.1 M |
| Residual train control | $4.1 M | $2.0 M | $2.0 M |
| Charging microgrids | $8.6 M | $3.4 M | $5.1 M |
| EPC / project services | $92.1 M | $13.8 M | $78.3 M |
| Shared national trainset factory | $321.0 M | $64.2 M | $256.8 M |
| **Total** | **$1.48 B** | **$296.3 M** | **$1.19 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Conakry](Conakry/README.md) | 2,010,000 | 87 | $1.14 B | $228.7 M | $912.5 M |

## Local Basis And Regeneration

Country finance parameters use `GN` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
