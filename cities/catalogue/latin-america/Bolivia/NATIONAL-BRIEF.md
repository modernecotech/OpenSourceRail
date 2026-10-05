# Bolivia National OpenSourceRail Strategy

This page contains only Bolivia-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$6.43 B (88.9%) of external capital** and **$7.90 B of external interest**. Capital plus saved interest totals **$14.33 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 1,815,000 |
| Trainsets / vehicle modules | 262 / 1,048 |
| City infrastructure and fleet CAPEX | $3.15 B |
| Shared national factory | $809.0 M |
| Factory sizing basis | 1,048 modules for La Paz, then reused nationally |
| **Total national programme** | **$4.02 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $804.5 M (20.0%) |
| Domestic / local capital | $3.21 B (80.0%) |
| Annual external capital draw | $160.9 M / yr |
| Annual local capital draw | $642.5 M / yr |
| Annual public construction commitment | $434.6 M / yr for 5 years |
| Annual post-grace debt service | $324.4 M / yr |
| Default foreign-turnkey external capital | $7.23 B |
| External capital saved | $6.43 B |
| Capital + lifetime external interest saved | $14.33 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $1.90 B | $284.3 M | $1.61 B |
| Stations | $415.0 M | $83.0 M | $332.0 M |
| Depots | $119.6 M | $29.9 M | $89.7 M |
| Rolling stock | $293.4 M | $102.7 M | $190.7 M |
| Dedicated solar plants | $205.1 M | $92.3 M | $112.8 M |
| Residual train control | $9.8 M | $4.9 M | $4.9 M |
| Charging microgrids | $20.6 M | $8.2 M | $12.3 M |
| EPC / project services | $249.4 M | $37.4 M | $212.0 M |
| Shared national trainset factory | $809.0 M | $161.8 M | $647.2 M |
| **Total** | **$4.02 B** | **$804.5 M** | **$3.21 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [La Paz](La-Paz/README.md) | 1,815,000 | 262 | $3.15 B | $634.2 M | $2.52 B |

## Local Basis And Regeneration

Country finance parameters use `BO` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
