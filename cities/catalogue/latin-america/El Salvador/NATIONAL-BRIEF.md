# El Salvador National OpenSourceRail Strategy

This page contains only El Salvador-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$6.64 B (88.7%) of external capital** and **$8.17 B of external interest**. Capital plus saved interest totals **$14.81 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 1,800,000 |
| Trainsets / vehicle modules | 294 / 1,176 |
| City infrastructure and fleet CAPEX | $3.31 B |
| Shared national factory | $794.6 M |
| Factory sizing basis | 1,176 modules for San Salvador, then reused nationally |
| **Total national programme** | **$4.16 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $846.4 M (20.3%) |
| Domestic / local capital | $3.31 B (79.7%) |
| Annual external capital draw | $169.3 M / yr |
| Annual local capital draw | $662.9 M / yr |
| Annual public construction commitment | $475.6 M / yr for 5 years |
| Annual post-grace debt service | $360.3 M / yr |
| Default foreign-turnkey external capital | $7.49 B |
| External capital saved | $6.64 B |
| Capital + lifetime external interest saved | $14.81 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $2.01 B | $302.0 M | $1.71 B |
| Stations | $351.6 M | $70.3 M | $281.3 M |
| Depots | $127.1 M | $31.8 M | $95.3 M |
| Rolling stock | $329.3 M | $115.2 M | $214.0 M |
| Dedicated solar plants | $257.5 M | $115.9 M | $141.7 M |
| Residual train control | $11.6 M | $5.8 M | $5.8 M |
| Charging microgrids | $20.2 M | $8.1 M | $12.1 M |
| EPC / project services | $255.4 M | $38.3 M | $217.1 M |
| Shared national trainset factory | $794.6 M | $158.9 M | $635.7 M |
| **Total** | **$4.16 B** | **$846.4 M** | **$3.31 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [San Salvador](San-Salvador/README.md) | 1,800,000 | 294 | $3.31 B | $679.1 M | $2.63 B |

## Local Basis And Regeneration

Country finance parameters use `SV` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
