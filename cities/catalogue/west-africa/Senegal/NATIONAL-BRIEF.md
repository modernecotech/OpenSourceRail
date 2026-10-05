# Senegal National OpenSourceRail Strategy

This page contains only Senegal-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$7.37 B (88.0%) of external capital** and **$9.24 B of external interest**. Capital plus saved interest totals **$16.62 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 4,030,000 |
| Trainsets / vehicle modules | 382 / 2,292 |
| City infrastructure and fleet CAPEX | $3.98 B |
| Shared national factory | $628.1 M |
| Factory sizing basis | 2,292 modules for Dakar, then reused nationally |
| **Total national programme** | **$4.65 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.00 B (21.6%) |
| Domestic / local capital | $3.65 B (78.4%) |
| Annual external capital draw | $143.4 M / yr |
| Annual local capital draw | $521.6 M / yr |
| Annual public construction commitment | $397.7 M / yr for 7 years |
| Annual post-grace debt service | $325.2 M / yr |
| Default foreign-turnkey external capital | $8.38 B |
| External capital saved | $7.37 B |
| Capital + lifetime external interest saved | $16.62 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $1.85 B | $277.4 M | $1.57 B |
| Stations | $772.4 M | $154.5 M | $617.9 M |
| Depots | $168.4 M | $42.1 M | $126.3 M |
| Rolling stock | $641.8 M | $224.6 M | $417.1 M |
| Dedicated solar plants | $250.2 M | $112.6 M | $137.6 M |
| Residual train control | $10.5 M | $5.3 M | $5.3 M |
| Charging microgrids | $45.4 M | $18.2 M | $27.2 M |
| EPC / project services | $288.1 M | $43.2 M | $244.9 M |
| Shared national trainset factory | $628.1 M | $125.6 M | $502.5 M |
| **Total** | **$4.65 B** | **$1.00 B** | **$3.65 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Dakar](Dakar/README.md) | 4,030,000 | 382 | $3.98 B | $871.2 M | $3.11 B |

## Local Basis And Regeneration

Country finance parameters use `SN` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
