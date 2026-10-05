# DR Congo National OpenSourceRail Strategy

This page contains only DR Congo-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$20.81 B (88.3%) of external capital** and **$26.88 B of external interest**. Capital plus saved interest totals **$47.68 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 7 |
| Represented population | 27,007,000 |
| Trainsets / vehicle modules | 1,212 / 5,669 |
| City infrastructure and fleet CAPEX | $12.57 B |
| Shared national factory | $490.0 M |
| Factory sizing basis | 3,378 modules for Kinshasa, then reused nationally |
| **Total national programme** | **$13.09 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $2.76 B (21.1%) |
| Domestic / local capital | $10.33 B (78.9%) |
| Annual external capital draw | $275.7 M / yr |
| Annual local capital draw | $1.03 B / yr |
| Annual public construction commitment | $1.41 B / yr for 10 years |
| Annual post-grace debt service | $1.27 B / yr |
| Default foreign-turnkey external capital | $23.56 B |
| External capital saved | $20.81 B |
| Capital + lifetime external interest saved | $47.68 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $7.43 B | $1.11 B | $6.32 B |
| Stations | $1.06 B | $212.8 M | $851.2 M |
| Depots | $582.5 M | $145.6 M | $436.9 M |
| Rolling stock | $1.61 B | $562.0 M | $1.04 B |
| Dedicated solar plants | $1.01 B | $456.4 M | $557.8 M |
| Residual train control | $37.0 M | $18.5 M | $18.5 M |
| Charging microgrids | $77.0 M | $30.8 M | $46.2 M |
| EPC / project services | $790.0 M | $118.5 M | $671.5 M |
| Shared national trainset factory | $490.0 M | $98.0 M | $392.0 M |
| **Total** | **$13.09 B** | **$2.76 B** | **$10.33 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Kinshasa](Kinshasa/README.md) | 17,178,000 | 563 | $5.91 B | $1.34 B | $4.57 B |
| [Lubumbashi](Lubumbashi/README.md) | 2,829,000 | 142 | $1.65 B | $333.5 M | $1.32 B |
| [Mbuji Mayi](Mbuji-Mayi/README.md) | 2,500,000 | 126 | $1.52 B | $307.2 M | $1.21 B |
| [Kisangani](Kisangani/README.md) | 1,300,000 | 43 | $551.1 M | $109.9 M | $441.2 M |
| [Kananga](Kananga/README.md) | 1,200,000 | 33 | $1.38 B | $229.5 M | $1.15 B |
| [Bukavu](Bukavu/README.md) | 1,000,000 | 159 | $797.0 M | $170.7 M | $626.3 M |
| [Goma](Goma/README.md) | 1,000,000 | 146 | $752.9 M | $160.1 M | $592.9 M |

## Local Basis And Regeneration

Country finance parameters use `CD` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
