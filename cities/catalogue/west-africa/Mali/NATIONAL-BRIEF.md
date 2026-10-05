# Mali National OpenSourceRail Strategy

This page contains only Mali-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$17.63 B (90.5%) of external capital** and **$22.77 B of external interest**. Capital plus saved interest totals **$40.40 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 2,929,000 |
| Trainsets / vehicle modules | 328 / 1,312 |
| City infrastructure and fleet CAPEX | $9.83 B |
| Shared national factory | $927.4 M |
| Factory sizing basis | 1,312 modules for Bamako, then reused nationally |
| **Total national programme** | **$10.82 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.85 B (17.1%) |
| Domestic / local capital | $8.97 B (82.9%) |
| Annual external capital draw | $184.6 M / yr |
| Annual local capital draw | $897.4 M / yr |
| Annual public construction commitment | $944.5 M / yr for 10 years |
| Annual post-grace debt service | $843.3 M / yr |
| Default foreign-turnkey external capital | $19.48 B |
| External capital saved | $17.63 B |
| Capital + lifetime external interest saved | $40.40 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $7.90 B | $1.19 B | $6.72 B |
| Stations | $586.2 M | $117.2 M | $469.0 M |
| Depots | $133.2 M | $33.3 M | $99.9 M |
| Rolling stock | $367.4 M | $128.6 M | $238.8 M |
| Dedicated solar plants | $164.4 M | $74.0 M | $90.4 M |
| Residual train control | $11.1 M | $5.6 M | $5.6 M |
| Charging microgrids | $28.6 M | $11.5 M | $17.2 M |
| EPC / project services | $697.1 M | $104.6 M | $592.5 M |
| Shared national trainset factory | $927.4 M | $185.5 M | $741.9 M |
| **Total** | **$10.82 B** | **$1.85 B** | **$8.97 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Bamako](Bamako/README.md) | 2,929,000 | 328 | $9.83 B | $1.65 B | $8.18 B |

## Local Basis And Regeneration

Country finance parameters use `ML` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
