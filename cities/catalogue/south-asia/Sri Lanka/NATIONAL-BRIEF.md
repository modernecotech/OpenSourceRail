# Sri Lanka National OpenSourceRail Strategy

This page contains only Sri Lanka-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$8.39 B (85.7%) of external capital** and **$10.52 B of external interest**. Capital plus saved interest totals **$18.92 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 4 |
| Represented population | 7,398,000 |
| Trainsets / vehicle modules | 983 / 4,440 |
| City infrastructure and fleet CAPEX | $5.25 B |
| Shared national factory | $178.9 M |
| Factory sizing basis | 2,982 modules for Colombo, then reused nationally |
| **Total national programme** | **$5.44 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.40 B (25.7%) |
| Domestic / local capital | $4.04 B (74.3%) |
| Annual external capital draw | $199.9 M / yr |
| Annual local capital draw | $577.3 M / yr |
| Annual public construction commitment | $614.9 M / yr for 7 years |
| Annual post-grace debt service | $525.4 M / yr |
| Default foreign-turnkey external capital | $9.79 B |
| External capital saved | $8.39 B |
| Capital + lifetime external interest saved | $18.92 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $1.77 B | $266.1 M | $1.51 B |
| Stations | $986.0 M | $197.2 M | $788.8 M |
| Depots | $32.0 M | $8.0 M | $24.0 M |
| Rolling stock | $1.27 B | $445.3 M | $827.0 M |
| Dedicated solar plants | $816.7 M | $367.5 M | $449.2 M |
| Residual train control | $25.7 M | $12.8 M | $12.8 M |
| Charging microgrids | $52.4 M | $20.9 M | $31.4 M |
| EPC / project services | $302.5 M | $45.4 M | $257.1 M |
| Shared national trainset factory | $178.9 M | $35.8 M | $143.1 M |
| **Total** | **$5.44 B** | **$1.40 B** | **$4.04 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Colombo](Colombo/README.md) | 5,648,000 | 497 | $3.59 B | $946.0 M | $2.65 B |
| [Kandy](Kandy/README.md) | 650,000 | 178 | $652.4 M | $160.5 M | $491.8 M |
| [Jaffna](Jaffna/README.md) | 600,000 | 131 | $456.8 M | $114.8 M | $342.0 M |
| [Galle](Galle/README.md) | 500,000 | 177 | $545.6 M | $140.0 M | $405.6 M |

## Local Basis And Regeneration

Country finance parameters use `LK` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
