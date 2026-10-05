# Senegal National OpenSourceRail Strategy

This page contains only Senegal-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$41.32 B (91.0%) of external capital** and **$51.79 B of external interest**. Capital plus saved interest totals **$93.11 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 4,030,000 |
| Trainsets / vehicle modules | 382 / 2,292 |
| City infrastructure and fleet CAPEX | $24.55 B |
| Shared national factory | $628.1 M |
| Factory sizing basis | 2,292 modules for Dakar, then reused nationally |
| **Total national programme** | **$25.22 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $4.09 B (16.2%) |
| Domestic / local capital | $21.14 B (83.8%) |
| Annual external capital draw | $584.2 M / yr |
| Annual local capital draw | $3.02 B / yr |
| Annual public construction commitment | $2.23 B / yr for 7 years |
| Annual post-grace debt service | $1.78 B / yr |
| Default foreign-turnkey external capital | $45.40 B |
| External capital saved | $41.32 B |
| Capital + lifetime external interest saved | $93.11 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $21.07 B | $3.16 B | $17.91 B |
| Stations | $772.4 M | $154.5 M | $617.9 M |
| Depots | $168.4 M | $42.1 M | $126.3 M |
| Rolling stock | $641.8 M | $224.6 M | $417.1 M |
| Dedicated solar plants | $250.2 M | $112.6 M | $137.6 M |
| Residual train control | $10.5 M | $5.3 M | $5.3 M |
| Charging microgrids | $45.4 M | $18.2 M | $27.2 M |
| EPC / project services | $1.63 B | $245.1 M | $1.39 B |
| Shared national trainset factory | $628.1 M | $125.6 M | $502.5 M |
| **Total** | **$25.22 B** | **$4.09 B** | **$21.14 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Dakar](Dakar/README.md) | 4,030,000 | 382 | $24.55 B | $3.96 B | $20.60 B |

## Local Basis And Regeneration

Country finance parameters use `SN` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
