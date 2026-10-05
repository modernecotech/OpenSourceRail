# Niger National OpenSourceRail Strategy

This page contains only Niger-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$14.62 B (90.8%) of external capital** and **$18.88 B of external interest**. Capital plus saved interest totals **$33.50 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 1,407,635 |
| Trainsets / vehicle modules | 197 / 788 |
| City infrastructure and fleet CAPEX | $8.27 B |
| Shared national factory | $629.7 M |
| Factory sizing basis | 788 modules for Niamey, then reused nationally |
| **Total national programme** | **$8.94 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.48 B (16.5%) |
| Domestic / local capital | $7.46 B (83.5%) |
| Annual external capital draw | $148.0 M / yr |
| Annual local capital draw | $746.4 M / yr |
| Annual public construction commitment | $753.2 M / yr for 10 years |
| Annual post-grace debt service | $672.0 M / yr |
| Default foreign-turnkey external capital | $16.10 B |
| External capital saved | $14.62 B |
| Capital + lifetime external interest saved | $33.50 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $6.93 B | $1.04 B | $5.89 B |
| Stations | $358.7 M | $71.7 M | $287.0 M |
| Depots | $107.7 M | $26.9 M | $80.7 M |
| Rolling stock | $220.6 M | $77.2 M | $143.4 M |
| Dedicated solar plants | $89.1 M | $40.1 M | $49.0 M |
| Residual train control | $7.1 M | $3.5 M | $3.5 M |
| Charging microgrids | $19.1 M | $7.6 M | $11.4 M |
| EPC / project services | $579.3 M | $86.9 M | $492.4 M |
| Shared national trainset factory | $629.7 M | $125.9 M | $503.8 M |
| **Total** | **$8.94 B** | **$1.48 B** | **$7.46 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Niamey](Niamey/README.md) | 1,407,635 | 197 | $8.27 B | $1.35 B | $6.92 B |

## Local Basis And Regeneration

Country finance parameters use `NE` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
