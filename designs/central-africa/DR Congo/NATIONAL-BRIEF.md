# DR Congo National OpenSourceRail Strategy

This page contains only DR Congo-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$12.95 B (85.9%) of external capital** and **$16.73 B of external interest**. Capital plus saved interest totals **$29.68 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 7 |
| Represented population | 27,007,000 |
| Trainsets / vehicle modules | 1,280 / 6,151 |
| City infrastructure and fleet CAPEX | $8.13 B |
| Shared national factory | $231.5 M |
| Factory sizing basis | 3,858 modules for Kinshasa, then reused nationally |
| **Total national programme** | **$8.38 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $2.13 B (25.4%) |
| Domestic / local capital | $6.25 B (74.6%) |
| Annual external capital draw | $212.8 M / yr |
| Annual local capital draw | $624.9 M / yr |
| Annual public construction commitment | $870.7 M / yr for 10 years |
| Annual post-grace debt service | $797.6 M / yr |
| Default foreign-turnkey external capital | $15.08 B |
| External capital saved | $12.95 B |
| Capital + lifetime external interest saved | $29.68 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $2.79 B | $418.0 M | $2.37 B |
| Stations | $1.68 B | $336.6 M | $1.35 B |
| Depots | $56.0 M | $14.0 M | $42.0 M |
| Rolling stock | $1.74 B | $608.2 M | $1.13 B |
| Dedicated solar plants | $1.27 B | $573.7 M | $701.2 M |
| Residual train control | $42.9 M | $21.4 M | $21.4 M |
| Charging microgrids | $100.4 M | $40.2 M | $60.2 M |
| EPC / project services | $464.7 M | $69.7 M | $395.0 M |
| Shared national trainset factory | $231.5 M | $46.3 M | $185.2 M |
| **Total** | **$8.38 B** | **$2.13 B** | **$6.25 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Kinshasa](Kinshasa/README.md) | 17,178,000 | 643 | $4.37 B | $1.17 B | $3.20 B |
| [Lubumbashi](Lubumbashi/README.md) | 2,829,000 | 161 | $1.01 B | $249.4 M | $765.0 M |
| [Mbuji Mayi](Mbuji-Mayi/README.md) | 2,500,000 | 135 | $1.07 B | $250.9 M | $817.3 M |
| [Kisangani](Kisangani/README.md) | 1,300,000 | 50 | $405.4 M | $94.8 M | $310.6 M |
| [Kananga](Kananga/README.md) | 1,200,000 | 36 | $298.5 M | $69.0 M | $229.5 M |
| [Bukavu](Bukavu/README.md) | 1,000,000 | 130 | $475.2 M | $119.7 M | $355.5 M |
| [Goma](Goma/README.md) | 1,000,000 | 125 | $499.7 M | $123.2 M | $376.5 M |

## Local Basis And Regeneration

Country finance parameters use `CD` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 scripts/generate-national-briefs.py
```
