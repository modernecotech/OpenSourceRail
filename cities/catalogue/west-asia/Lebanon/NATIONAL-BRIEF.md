# Lebanon National OpenSourceRail Strategy

This page contains only Lebanon-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$5.82 B (88.7%) of external capital** and **$7.37 B of external interest**. Capital plus saved interest totals **$13.20 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 3 |
| Represented population | 3,230,000 |
| Trainsets / vehicle modules | 374 / 1,255 |
| City infrastructure and fleet CAPEX | $3.00 B |
| Shared national factory | $603.9 M |
| Factory sizing basis | 760 modules for Beirut, then reused nationally |
| **Total national programme** | **$3.65 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $739.9 M (20.3%) |
| Domestic / local capital | $2.91 B (79.7%) |
| Annual external capital draw | $92.5 M / yr |
| Annual local capital draw | $363.3 M / yr |
| Annual public construction commitment | $687.3 M / yr for 8 years |
| Annual post-grace debt service | $625.9 M / yr |
| Default foreign-turnkey external capital | $6.56 B |
| External capital saved | $5.82 B |
| Capital + lifetime external interest saved | $13.20 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $1.62 B | $243.4 M | $1.38 B |
| Stations | $470.8 M | $94.2 M | $376.6 M |
| Depots | $201.2 M | $50.3 M | $150.9 M |
| Rolling stock | $359.0 M | $125.7 M | $233.4 M |
| Dedicated solar plants | $130.1 M | $58.5 M | $71.5 M |
| Residual train control | $9.5 M | $4.7 M | $4.7 M |
| Charging microgrids | $19.6 M | $7.9 M | $11.8 M |
| EPC / project services | $230.1 M | $34.5 M | $195.5 M |
| Shared national trainset factory | $603.9 M | $120.8 M | $483.1 M |
| **Total** | **$3.65 B** | **$739.9 M** | **$2.91 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Beirut](Beirut/README.md) | 2,200,000 | 190 | $1.93 B | $397.7 M | $1.53 B |
| [Tripoli Lb](Tripoli-Lb/README.md) | 730,000 | 127 | $706.2 M | $146.4 M | $559.8 M |
| [Sidon](Sidon/README.md) | 300,000 | 57 | $361.7 M | $68.6 M | $293.0 M |

## Local Basis And Regeneration

Country finance parameters use `LB` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
