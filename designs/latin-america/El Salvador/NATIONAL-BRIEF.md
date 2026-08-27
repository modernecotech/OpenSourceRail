# El Salvador National OpenSourceRail Strategy

This page contains only El Salvador-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$3.42 B (86.6%) of external capital** and **$4.21 B of external interest**. Capital plus saved interest totals **$7.63 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 1,800,000 |
| Trainsets / vehicle modules | 308 / 1,232 |
| City infrastructure and fleet CAPEX | $2.12 B |
| Shared national factory | $73.9 M |
| Factory sizing basis | 1,232 modules for San Salvador, then reused nationally |
| **Total national programme** | **$2.19 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $530.0 M (24.1%) |
| Domestic / local capital | $1.66 B (75.9%) |
| Annual external capital draw | $106.0 M / yr |
| Annual local capital draw | $332.9 M / yr |
| Annual public construction commitment | $243.6 M / yr for 5 years |
| Annual post-grace debt service | $187.0 M / yr |
| Default foreign-turnkey external capital | $3.95 B |
| External capital saved | $3.42 B |
| Capital + lifetime external interest saved | $7.63 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $831.8 M | $124.8 M | $707.0 M |
| Stations | $464.0 M | $92.8 M | $371.2 M |
| Depots | $8.0 M | $2.0 M | $6.0 M |
| Rolling stock | $345.0 M | $120.7 M | $224.2 M |
| Dedicated solar plants | $312.4 M | $140.6 M | $171.8 M |
| Residual train control | $12.8 M | $6.4 M | $6.4 M |
| Charging microgrids | $23.6 M | $9.4 M | $14.1 M |
| EPC / project services | $123.1 M | $18.5 M | $104.7 M |
| Shared national trainset factory | $73.9 M | $14.8 M | $59.1 M |
| **Total** | **$2.19 B** | **$530.0 M** | **$1.66 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [San Salvador](San-Salvador/README.md) | 1,800,000 | 308 | $2.12 B | $514.4 M | $1.60 B |

## Local Basis And Regeneration

Country finance parameters use `SV` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 scripts/generate-national-briefs.py
```
