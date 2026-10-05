# Tunisia National OpenSourceRail Strategy

This page contains only Tunisia-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$17.55 B (90.7%) of external capital** and **$21.58 B of external interest**. Capital plus saved interest totals **$39.13 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 2,900,000 |
| Trainsets / vehicle modules | 246 / 984 |
| City infrastructure and fleet CAPEX | $9.92 B |
| Shared national factory | $769.6 M |
| Factory sizing basis | 984 modules for Tunis, then reused nationally |
| **Total national programme** | **$10.75 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.80 B (16.7%) |
| Domestic / local capital | $8.95 B (83.3%) |
| Annual external capital draw | $359.2 M / yr |
| Annual local capital draw | $1.79 B / yr |
| Annual public construction commitment | $1.08 B / yr for 5 years |
| Annual post-grace debt service | $780.6 M / yr |
| Default foreign-turnkey external capital | $19.35 B |
| External capital saved | $17.55 B |
| Capital + lifetime external interest saved | $39.13 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $8.36 B | $1.25 B | $7.11 B |
| Stations | $331.0 M | $66.2 M | $264.8 M |
| Depots | $104.6 M | $26.1 M | $78.4 M |
| Rolling stock | $275.5 M | $96.4 M | $179.1 M |
| Dedicated solar plants | $181.4 M | $81.7 M | $99.8 M |
| Residual train control | $10.1 M | $5.0 M | $5.0 M |
| Charging microgrids | $19.9 M | $8.0 M | $12.0 M |
| EPC / project services | $691.3 M | $103.7 M | $587.6 M |
| Shared national trainset factory | $769.6 M | $153.9 M | $615.7 M |
| **Total** | **$10.75 B** | **$1.80 B** | **$8.95 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Tunis](Tunis/README.md) | 2,900,000 | 246 | $9.92 B | $1.63 B | $8.29 B |

## Local Basis And Regeneration

Country finance parameters use `TN` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
