# Guinea National OpenSourceRail Strategy

This page contains only Guinea-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$16.09 B (91.2%) of external capital** and **$20.78 B of external interest**. Capital plus saved interest totals **$36.88 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 2,010,000 |
| Trainsets / vehicle modules | 87 / 348 |
| City infrastructure and fleet CAPEX | $9.45 B |
| Shared national factory | $321.0 M |
| Factory sizing basis | 348 modules for Conakry, then reused nationally |
| **Total national programme** | **$9.80 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.54 B (15.8%) |
| Domestic / local capital | $8.25 B (84.2%) |
| Annual external capital draw | $154.3 M / yr |
| Annual local capital draw | $825.3 M / yr |
| Annual public construction commitment | $894.8 M / yr for 10 years |
| Annual post-grace debt service | $795.1 M / yr |
| Default foreign-turnkey external capital | $17.63 B |
| External capital saved | $16.09 B |
| Capital + lifetime external interest saved | $36.88 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $8.47 B | $1.27 B | $7.20 B |
| Stations | $126.1 M | $25.2 M | $100.9 M |
| Depots | $52.3 M | $13.1 M | $39.2 M |
| Rolling stock | $97.4 M | $34.1 M | $63.3 M |
| Dedicated solar plants | $76.5 M | $34.4 M | $42.1 M |
| Residual train control | $4.1 M | $2.0 M | $2.0 M |
| Charging microgrids | $8.6 M | $3.4 M | $5.1 M |
| EPC / project services | $635.9 M | $95.4 M | $540.5 M |
| Shared national trainset factory | $321.0 M | $64.2 M | $256.8 M |
| **Total** | **$9.80 B** | **$1.54 B** | **$8.25 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Conakry](Conakry/README.md) | 2,010,000 | 87 | $9.45 B | $1.48 B | $7.98 B |

## Local Basis And Regeneration

Country finance parameters use `GN` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
