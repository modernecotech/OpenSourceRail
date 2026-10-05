# Niger National OpenSourceRail Strategy

This page contains only Niger-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$4.80 B (89.1%) of external capital** and **$6.20 B of external interest**. Capital plus saved interest totals **$11.01 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 1,407,635 |
| Trainsets / vehicle modules | 197 / 788 |
| City infrastructure and fleet CAPEX | $2.32 B |
| Shared national factory | $629.7 M |
| Factory sizing basis | 788 modules for Niamey, then reused nationally |
| **Total national programme** | **$2.99 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $587.5 M (19.6%) |
| Domestic / local capital | $2.41 B (80.4%) |
| Annual external capital draw | $58.8 M / yr |
| Annual local capital draw | $240.7 M / yr |
| Annual public construction commitment | $247.9 M / yr for 10 years |
| Annual post-grace debt service | $223.5 M / yr |
| Default foreign-turnkey external capital | $5.39 B |
| External capital saved | $4.80 B |
| Capital + lifetime external interest saved | $11.01 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $1.37 B | $205.9 M | $1.17 B |
| Stations | $358.7 M | $71.7 M | $287.0 M |
| Depots | $107.7 M | $26.9 M | $80.7 M |
| Rolling stock | $220.6 M | $77.2 M | $143.4 M |
| Dedicated solar plants | $89.1 M | $40.1 M | $49.0 M |
| Residual train control | $7.1 M | $3.5 M | $3.5 M |
| Charging microgrids | $19.1 M | $7.6 M | $11.4 M |
| EPC / project services | $190.1 M | $28.5 M | $161.6 M |
| Shared national trainset factory | $629.7 M | $125.9 M | $503.8 M |
| **Total** | **$2.99 B** | **$587.5 M** | **$2.41 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Niamey](Niamey/README.md) | 1,407,635 | 197 | $2.32 B | $455.0 M | $1.87 B |

## Local Basis And Regeneration

Country finance parameters use `NE` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
