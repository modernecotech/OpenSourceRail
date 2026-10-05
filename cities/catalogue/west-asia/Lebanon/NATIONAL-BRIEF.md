# Lebanon National OpenSourceRail Strategy

This page contains only Lebanon-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$14.40 B (90.5%) of external capital** and **$18.23 B of external interest**. Capital plus saved interest totals **$32.62 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 3 |
| Represented population | 3,230,000 |
| Trainsets / vehicle modules | 374 / 1,255 |
| City infrastructure and fleet CAPEX | $8.20 B |
| Shared national factory | $603.9 M |
| Factory sizing basis | 760 modules for Beirut, then reused nationally |
| **Total national programme** | **$8.84 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.52 B (17.2%) |
| Domestic / local capital | $7.32 B (82.8%) |
| Annual external capital draw | $189.9 M / yr |
| Annual local capital draw | $915.4 M / yr |
| Annual public construction commitment | $1.72 B / yr for 8 years |
| Annual post-grace debt service | $1.56 B / yr |
| Default foreign-turnkey external capital | $15.92 B |
| External capital saved | $14.40 B |
| Capital + lifetime external interest saved | $32.62 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $6.48 B | $971.8 M | $5.51 B |
| Stations | $470.8 M | $94.2 M | $376.6 M |
| Depots | $201.2 M | $50.3 M | $150.9 M |
| Rolling stock | $359.0 M | $125.7 M | $233.4 M |
| Dedicated solar plants | $130.1 M | $58.5 M | $71.5 M |
| Residual train control | $9.5 M | $4.7 M | $4.7 M |
| Charging microgrids | $19.6 M | $7.9 M | $11.8 M |
| EPC / project services | $570.0 M | $85.5 M | $484.5 M |
| Shared national trainset factory | $603.9 M | $120.8 M | $483.1 M |
| **Total** | **$8.84 B** | **$1.52 B** | **$7.32 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Beirut](Beirut/README.md) | 2,200,000 | 190 | $6.82 B | $1.13 B | $5.69 B |
| [Tripoli Lb](Tripoli-Lb/README.md) | 730,000 | 127 | $1.02 B | $193.3 M | $825.4 M |
| [Sidon](Sidon/README.md) | 300,000 | 57 | $361.7 M | $68.6 M | $293.0 M |

## Local Basis And Regeneration

Country finance parameters use `LB` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
