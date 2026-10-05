# Sri Lanka National OpenSourceRail Strategy

This page contains only Sri Lanka-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$13.71 B (87.8%) of external capital** and **$17.19 B of external interest**. Capital plus saved interest totals **$30.90 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 4 |
| Represented population | 7,398,000 |
| Trainsets / vehicle modules | 1,003 / 4,455 |
| City infrastructure and fleet CAPEX | $8.05 B |
| Shared national factory | $584.4 M |
| Factory sizing basis | 2,892 modules for Colombo, then reused nationally |
| **Total national programme** | **$8.67 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.90 B (21.9%) |
| Domestic / local capital | $6.77 B (78.1%) |
| Annual external capital draw | $271.8 M / yr |
| Annual local capital draw | $967.4 M / yr |
| Annual public construction commitment | $1.01 B / yr for 7 years |
| Annual post-grace debt service | $854.5 M / yr |
| Default foreign-turnkey external capital | $15.61 B |
| External capital saved | $13.71 B |
| Capital + lifetime external interest saved | $30.90 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $3.96 B | $594.6 M | $3.37 B |
| Stations | $1.19 B | $237.0 M | $948.2 M |
| Depots | $410.4 M | $102.6 M | $307.8 M |
| Rolling stock | $1.28 B | $447.5 M | $831.1 M |
| Dedicated solar plants | $643.2 M | $289.5 M | $353.8 M |
| Residual train control | $22.7 M | $11.3 M | $11.3 M |
| Charging microgrids | $60.5 M | $24.2 M | $36.3 M |
| EPC / project services | $525.4 M | $78.8 M | $446.6 M |
| Shared national trainset factory | $584.4 M | $116.9 M | $467.5 M |
| **Total** | **$8.67 B** | **$1.90 B** | **$6.77 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Colombo](Colombo/README.md) | 5,648,000 | 482 | $5.27 B | $1.19 B | $4.08 B |
| [Kandy](Kandy/README.md) | 650,000 | 195 | $1.12 B | $231.8 M | $884.1 M |
| [Jaffna](Jaffna/README.md) | 600,000 | 145 | $745.9 M | $160.0 M | $585.9 M |
| [Galle](Galle/README.md) | 500,000 | 181 | $914.5 M | $196.4 M | $718.1 M |

## Local Basis And Regeneration

Country finance parameters use `LK` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
