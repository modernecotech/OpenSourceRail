# Bolivia National OpenSourceRail Strategy

This page contains only Bolivia-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$6.08 B (88.9%) of external capital** and **$7.47 B of external interest**. Capital plus saved interest totals **$13.55 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 1,815,000 |
| Trainsets / vehicle modules | 249 / 996 |
| City infrastructure and fleet CAPEX | $2.97 B |
| Shared national factory | $774.3 M |
| Factory sizing basis | 996 modules for La Paz, then reused nationally |
| **Total national programme** | **$3.80 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $759.4 M (20.0%) |
| Domestic / local capital | $3.04 B (80.0%) |
| Annual external capital draw | $151.9 M / yr |
| Annual local capital draw | $608.0 M / yr |
| Annual public construction commitment | $411.1 M / yr for 5 years |
| Annual post-grace debt service | $306.9 M / yr |
| Default foreign-turnkey external capital | $6.84 B |
| External capital saved | $6.08 B |
| Capital + lifetime external interest saved | $13.55 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $1.88 B | $281.4 M | $1.59 B |
| Stations | $285.5 M | $57.1 M | $228.4 M |
| Depots | $118.7 M | $29.7 M | $89.0 M |
| Rolling stock | $278.9 M | $97.6 M | $181.3 M |
| Dedicated solar plants | $203.5 M | $91.6 M | $111.9 M |
| Residual train control | $9.6 M | $4.8 M | $4.8 M |
| Charging microgrids | $17.6 M | $7.0 M | $10.5 M |
| EPC / project services | $235.2 M | $35.3 M | $200.0 M |
| Shared national trainset factory | $774.3 M | $154.9 M | $619.5 M |
| **Total** | **$3.80 B** | **$759.4 M** | **$3.04 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [La Paz](La-Paz/README.md) | 1,815,000 | 249 | $2.97 B | $596.4 M | $2.37 B |

## Local Basis And Regeneration

Country finance parameters use `BO` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
