# Jordan National OpenSourceRail Strategy

This page contains only Jordan-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$12.50 B (88.1%) of external capital** and **$15.36 B of external interest**. Capital plus saved interest totals **$27.86 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 4 |
| Represented population | 5,557,000 |
| Trainsets / vehicle modules | 863 / 3,963 |
| City infrastructure and fleet CAPEX | $7.23 B |
| Shared national factory | $603.5 M |
| Factory sizing basis | 2,874 modules for Amman, then reused nationally |
| **Total national programme** | **$7.88 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.68 B (21.3%) |
| Domestic / local capital | $6.20 B (78.7%) |
| Annual external capital draw | $336.0 M / yr |
| Annual local capital draw | $1.24 B / yr |
| Annual public construction commitment | $695.2 M / yr for 5 years |
| Annual post-grace debt service | $500.1 M / yr |
| Default foreign-turnkey external capital | $14.18 B |
| External capital saved | $12.50 B |
| Capital + lifetime external interest saved | $27.86 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $4.02 B | $603.2 M | $3.42 B |
| Stations | $681.0 M | $136.2 M | $544.8 M |
| Depots | $388.0 M | $97.0 M | $291.0 M |
| Rolling stock | $1.13 B | $395.1 M | $733.8 M |
| Dedicated solar plants | $502.3 M | $226.0 M | $276.2 M |
| Residual train control | $22.2 M | $11.1 M | $11.1 M |
| Charging microgrids | $46.1 M | $18.5 M | $27.7 M |
| EPC / project services | $482.4 M | $72.4 M | $410.0 M |
| Shared national trainset factory | $603.5 M | $120.7 M | $482.8 M |
| **Total** | **$7.88 B** | **$1.68 B** | **$6.20 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Amman](Amman/README.md) | 4,007,000 | 479 | $5.08 B | $1.12 B | $3.96 B |
| [Zarqa](Zarqa/README.md) | 700,000 | 202 | $1.11 B | $227.9 M | $885.4 M |
| [Irbid](Irbid/README.md) | 600,000 | 119 | $629.3 M | $131.3 M | $498.0 M |
| [Aqaba](Aqaba/README.md) | 250,000 | 63 | $407.2 M | $76.6 M | $330.6 M |

## Local Basis And Regeneration

Country finance parameters use `JO` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
