# Sri Lanka National OpenSourceRail Strategy

This page contains only Sri Lanka-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$28.63 B (89.8%) of external capital** and **$35.89 B of external interest**. Capital plus saved interest totals **$64.52 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 4 |
| Represented population | 7,398,000 |
| Trainsets / vehicle modules | 1,003 / 4,455 |
| City infrastructure and fleet CAPEX | $17.09 B |
| Shared national factory | $584.4 M |
| Factory sizing basis | 2,892 modules for Colombo, then reused nationally |
| **Total national programme** | **$17.72 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $3.26 B (18.4%) |
| Domestic / local capital | $14.46 B (81.6%) |
| Annual external capital draw | $465.5 M / yr |
| Annual local capital draw | $2.07 B / yr |
| Annual public construction commitment | $2.12 B / yr for 7 years |
| Annual post-grace debt service | $1.78 B / yr |
| Default foreign-turnkey external capital | $31.89 B |
| External capital saved | $28.63 B |
| Capital + lifetime external interest saved | $64.52 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $12.41 B | $1.86 B | $10.55 B |
| Stations | $1.19 B | $237.0 M | $948.2 M |
| Depots | $410.4 M | $102.6 M | $307.8 M |
| Rolling stock | $1.28 B | $447.5 M | $831.1 M |
| Dedicated solar plants | $643.2 M | $289.5 M | $353.8 M |
| Residual train control | $22.7 M | $11.3 M | $11.3 M |
| Charging microgrids | $60.5 M | $24.2 M | $36.3 M |
| EPC / project services | $1.12 B | $167.5 M | $949.4 M |
| Shared national trainset factory | $584.4 M | $116.9 M | $467.5 M |
| **Total** | **$17.72 B** | **$3.26 B** | **$14.46 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Colombo](Colombo/README.md) | 5,648,000 | 482 | $9.81 B | $1.87 B | $7.94 B |
| [Kandy](Kandy/README.md) | 650,000 | 195 | $1.13 B | $233.5 M | $893.7 M |
| [Jaffna](Jaffna/README.md) | 600,000 | 145 | $746.3 M | $160.1 M | $586.2 M |
| [Galle](Galle/README.md) | 500,000 | 181 | $5.41 B | $870.4 M | $4.54 B |

## Local Basis And Regeneration

Country finance parameters use `LK` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
