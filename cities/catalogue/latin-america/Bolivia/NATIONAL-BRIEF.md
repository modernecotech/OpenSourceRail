# Bolivia National OpenSourceRail Strategy

This page contains only Bolivia-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$6.42 B (88.9%) of external capital** and **$7.89 B of external interest**. Capital plus saved interest totals **$14.31 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 1,815,000 |
| Trainsets / vehicle modules | 262 / 1,048 |
| City infrastructure and fleet CAPEX | $3.15 B |
| Shared national factory | $809.0 M |
| Factory sizing basis | 1,048 modules for La Paz, then reused nationally |
| **Total national programme** | **$4.01 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $803.9 M (20.0%) |
| Domestic / local capital | $3.21 B (80.0%) |
| Annual external capital draw | $160.8 M / yr |
| Annual local capital draw | $641.8 M / yr |
| Annual public construction commitment | $434.1 M / yr for 5 years |
| Annual post-grace debt service | $324.0 M / yr |
| Default foreign-turnkey external capital | $7.22 B |
| External capital saved | $6.42 B |
| Capital + lifetime external interest saved | $14.31 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $1.89 B | $283.7 M | $1.61 B |
| Stations | $415.0 M | $83.0 M | $332.0 M |
| Depots | $119.6 M | $29.9 M | $89.7 M |
| Rolling stock | $293.4 M | $102.7 M | $190.7 M |
| Dedicated solar plants | $205.1 M | $92.3 M | $112.8 M |
| Residual train control | $9.8 M | $4.9 M | $4.9 M |
| Charging microgrids | $20.6 M | $8.2 M | $12.3 M |
| EPC / project services | $249.1 M | $37.4 M | $211.7 M |
| Shared national trainset factory | $809.0 M | $161.8 M | $647.2 M |
| **Total** | **$4.01 B** | **$803.9 M** | **$3.21 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [La Paz](La-Paz/README.md) | 1,815,000 | 262 | $3.15 B | $633.6 M | $2.51 B |

## Local Basis And Regeneration

Country finance parameters use `BO` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
