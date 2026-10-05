# DR Congo National OpenSourceRail Strategy

This page contains only DR Congo-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$162.15 B (90.9%) of external capital** and **$209.45 B of external interest**. Capital plus saved interest totals **$371.60 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 7 |
| Represented population | 27,007,000 |
| Trainsets / vehicle modules | 2,132 / 11,093 |
| City infrastructure and fleet CAPEX | $98.58 B |
| Shared national factory | $518.4 M |
| Factory sizing basis | 8,640 modules for Kinshasa, then reused nationally |
| **Total national programme** | **$99.14 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $16.30 B (16.4%) |
| Domestic / local capital | $82.84 B (83.6%) |
| Annual external capital draw | $1.63 B / yr |
| Annual local capital draw | $8.28 B / yr |
| Annual public construction commitment | $11.01 B / yr for 10 years |
| Annual post-grace debt service | $9.84 B / yr |
| Default foreign-turnkey external capital | $178.45 B |
| External capital saved | $162.15 B |
| Capital + lifetime external interest saved | $371.60 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $82.27 B | $12.34 B | $69.93 B |
| Stations | $4.38 B | $876.3 M | $3.51 B |
| Depots | $817.3 M | $204.3 M | $613.0 M |
| Rolling stock | $3.12 B | $1.09 B | $2.03 B |
| Dedicated solar plants | $1.35 B | $608.4 M | $743.6 M |
| Residual train control | $47.6 M | $23.8 M | $23.8 M |
| Charging microgrids | $229.6 M | $91.8 M | $137.8 M |
| EPC / project services | $6.40 B | $959.6 M | $5.44 B |
| Shared national trainset factory | $518.4 M | $103.7 M | $414.7 M |
| **Total** | **$99.14 B** | **$16.30 B** | **$82.84 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Kinshasa](Kinshasa/README.md) | 17,178,000 | 1,440 | $84.14 B | $13.69 B | $70.45 B |
| [Lubumbashi](Lubumbashi/README.md) | 2,829,000 | 154 | $1.79 B | $361.8 M | $1.42 B |
| [Mbuji Mayi](Mbuji-Mayi/README.md) | 2,500,000 | 131 | $1.54 B | $312.4 M | $1.23 B |
| [Kisangani](Kisangani/README.md) | 1,300,000 | 58 | $2.56 B | $419.8 M | $2.14 B |
| [Kananga](Kananga/README.md) | 1,200,000 | 34 | $5.30 B | $818.2 M | $4.48 B |
| [Bukavu](Bukavu/README.md) | 1,000,000 | 166 | $2.46 B | $424.3 M | $2.03 B |
| [Goma](Goma/README.md) | 1,000,000 | 149 | $790.8 M | $167.9 M | $622.9 M |

## Local Basis And Regeneration

Country finance parameters use `CD` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
