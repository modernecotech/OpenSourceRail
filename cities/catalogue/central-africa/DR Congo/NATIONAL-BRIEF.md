# DR Congo National OpenSourceRail Strategy

This page contains only DR Congo-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$31.82 B (87.7%) of external capital** and **$41.10 B of external interest**. Capital plus saved interest totals **$72.91 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 7 |
| Represented population | 27,007,000 |
| Trainsets / vehicle modules | 2,132 / 11,093 |
| City infrastructure and fleet CAPEX | $19.60 B |
| Shared national factory | $518.4 M |
| Factory sizing basis | 8,640 modules for Kinshasa, then reused nationally |
| **Total national programme** | **$20.15 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $4.45 B (22.1%) |
| Domestic / local capital | $15.70 B (77.9%) |
| Annual external capital draw | $445.4 M / yr |
| Annual local capital draw | $1.57 B / yr |
| Annual public construction commitment | $2.15 B / yr for 10 years |
| Annual post-grace debt service | $1.95 B / yr |
| Default foreign-turnkey external capital | $36.27 B |
| External capital saved | $31.82 B |
| Capital + lifetime external interest saved | $72.91 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $8.45 B | $1.27 B | $7.18 B |
| Stations | $4.38 B | $876.3 M | $3.51 B |
| Depots | $817.3 M | $204.3 M | $613.0 M |
| Rolling stock | $3.12 B | $1.09 B | $2.03 B |
| Dedicated solar plants | $1.35 B | $608.4 M | $743.6 M |
| Residual train control | $47.6 M | $23.8 M | $23.8 M |
| Charging microgrids | $229.6 M | $91.8 M | $137.8 M |
| EPC / project services | $1.23 B | $184.5 M | $1.05 B |
| Shared national trainset factory | $518.4 M | $103.7 M | $414.7 M |
| **Total** | **$20.15 B** | **$4.45 B** | **$15.70 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Kinshasa](Kinshasa/README.md) | 17,178,000 | 1,440 | $13.38 B | $3.07 B | $10.31 B |
| [Lubumbashi](Lubumbashi/README.md) | 2,829,000 | 154 | $1.76 B | $358.3 M | $1.40 B |
| [Mbuji Mayi](Mbuji-Mayi/README.md) | 2,500,000 | 131 | $1.54 B | $312.4 M | $1.23 B |
| [Kisangani](Kisangani/README.md) | 1,300,000 | 58 | $670.4 M | $136.3 M | $534.2 M |
| [Kananga](Kananga/README.md) | 1,200,000 | 34 | $546.5 M | $104.8 M | $441.7 M |
| [Bukavu](Bukavu/README.md) | 1,000,000 | 166 | $896.8 M | $190.3 M | $706.5 M |
| [Goma](Goma/README.md) | 1,000,000 | 149 | $789.7 M | $167.7 M | $622.0 M |

## Local Basis And Regeneration

Country finance parameters use `CD` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
