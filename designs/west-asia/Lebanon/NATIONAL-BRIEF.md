# Lebanon National OpenSourceRail Strategy

This page contains only Lebanon-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$3.22 B (87.0%) of external capital** and **$4.08 B of external interest**. Capital plus saved interest totals **$7.30 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 3 |
| Represented population | 3,230,000 |
| Trainsets / vehicle modules | 367 / 1,211 |
| City infrastructure and fleet CAPEX | $2.01 B |
| Shared national factory | $45.4 M |
| Factory sizing basis | 756 modules for Beirut, then reused nationally |
| **Total national programme** | **$2.06 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $479.5 M (23.3%) |
| Domestic / local capital | $1.58 B (76.7%) |
| Annual external capital draw | $59.9 M / yr |
| Annual local capital draw | $197.0 M / yr |
| Annual public construction commitment | $376.1 M / yr for 8 years |
| Annual post-grace debt service | $344.0 M / yr |
| Default foreign-turnkey external capital | $3.70 B |
| External capital saved | $3.22 B |
| Capital + lifetime external interest saved | $7.30 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $732.2 M | $109.8 M | $622.4 M |
| Stations | $552.9 M | $110.6 M | $442.3 M |
| Depots | $24.0 M | $6.0 M | $18.0 M |
| Rolling stock | $345.0 M | $120.8 M | $224.3 M |
| Dedicated solar plants | $202.9 M | $91.3 M | $111.6 M |
| Residual train control | $11.3 M | $5.6 M | $5.6 M |
| Charging microgrids | $20.4 M | $8.1 M | $12.2 M |
| EPC / project services | $121.2 M | $18.2 M | $103.0 M |
| Shared national trainset factory | $45.4 M | $9.1 M | $36.3 M |
| **Total** | **$2.06 B** | **$479.5 M** | **$1.58 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Beirut](Beirut/README.md) | 2,200,000 | 189 | $1.34 B | $313.9 M | $1.02 B |
| [Tripoli Lb](Tripoli-Lb/README.md) | 730,000 | 99 | $387.8 M | $93.7 M | $294.1 M |
| [Sidon](Sidon/README.md) | 300,000 | 79 | $283.0 M | $62.4 M | $220.6 M |

## Local Basis And Regeneration

Country finance parameters use `LB` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 scripts/generate-national-briefs.py
```
