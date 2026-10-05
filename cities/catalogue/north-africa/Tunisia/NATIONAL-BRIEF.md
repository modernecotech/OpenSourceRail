# Tunisia National OpenSourceRail Strategy

This page contains only Tunisia-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$5.74 B (89.0%) of external capital** and **$7.06 B of external interest**. Capital plus saved interest totals **$12.80 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 2,900,000 |
| Trainsets / vehicle modules | 230 / 920 |
| City infrastructure and fleet CAPEX | $2.82 B |
| Shared national factory | $715.7 M |
| Factory sizing basis | 920 modules for Tunis, then reused nationally |
| **Total national programme** | **$3.59 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $710.4 M (19.8%) |
| Domestic / local capital | $2.87 B (80.2%) |
| Annual external capital draw | $142.1 M / yr |
| Annual local capital draw | $575.0 M / yr |
| Annual public construction commitment | $354.0 M / yr for 5 years |
| Annual post-grace debt service | $258.3 M / yr |
| Default foreign-turnkey external capital | $6.45 B |
| External capital saved | $5.74 B |
| Capital + lifetime external interest saved | $12.80 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $1.81 B | $272.2 M | $1.54 B |
| Stations | $264.5 M | $52.9 M | $211.6 M |
| Depots | $102.6 M | $25.7 M | $77.0 M |
| Rolling stock | $257.6 M | $90.2 M | $167.4 M |
| Dedicated solar plants | $179.6 M | $80.8 M | $98.8 M |
| Residual train control | $9.9 M | $4.9 M | $4.9 M |
| Charging microgrids | $17.9 M | $7.1 M | $10.7 M |
| EPC / project services | $222.8 M | $33.4 M | $189.4 M |
| Shared national trainset factory | $715.7 M | $143.1 M | $572.5 M |
| **Total** | **$3.59 B** | **$710.4 M** | **$2.87 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Tunis](Tunis/README.md) | 2,900,000 | 230 | $2.82 B | $559.7 M | $2.26 B |

## Local Basis And Regeneration

Country finance parameters use `TN` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
