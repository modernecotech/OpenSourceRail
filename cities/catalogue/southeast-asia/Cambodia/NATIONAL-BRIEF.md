# Cambodia National OpenSourceRail Strategy

This page contains only Cambodia-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$8.31 B (88.9%) of external capital** and **$10.42 B of external interest**. Capital plus saved interest totals **$18.73 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 2,281,000 |
| Trainsets / vehicle modules | 374 / 1,496 |
| City infrastructure and fleet CAPEX | $4.62 B |
| Shared national factory | $534.3 M |
| Factory sizing basis | 1,496 modules for Phnom Penh, then reused nationally |
| **Total national programme** | **$5.19 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.03 B (19.9%) |
| Domestic / local capital | $4.16 B (80.1%) |
| Annual external capital draw | $147.5 M / yr |
| Annual local capital draw | $594.0 M / yr |
| Annual public construction commitment | $431.4 M / yr for 7 years |
| Annual post-grace debt service | $349.6 M / yr |
| Default foreign-turnkey external capital | $9.34 B |
| External capital saved | $8.31 B |
| Capital + lifetime external interest saved | $18.73 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $2.75 B | $413.0 M | $2.34 B |
| Stations | $703.5 M | $140.7 M | $562.8 M |
| Depots | $142.0 M | $35.5 M | $106.5 M |
| Rolling stock | $418.9 M | $146.6 M | $272.3 M |
| Dedicated solar plants | $272.8 M | $122.8 M | $150.1 M |
| Residual train control | $12.2 M | $6.1 M | $6.1 M |
| Charging microgrids | $31.4 M | $12.5 M | $18.8 M |
| EPC / project services | $321.7 M | $48.3 M | $273.5 M |
| Shared national trainset factory | $534.3 M | $106.9 M | $427.5 M |
| **Total** | **$5.19 B** | **$1.03 B** | **$4.16 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Phnom Penh](Phnom-Penh/README.md) | 2,281,000 | 374 | $4.62 B | $919.9 M | $3.70 B |

## Local Basis And Regeneration

Country finance parameters use `KH` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
