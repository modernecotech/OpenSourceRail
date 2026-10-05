# Nepal National OpenSourceRail Strategy

This page contains only Nepal-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$7.65 B (88.7%) of external capital** and **$9.59 B of external interest**. Capital plus saved interest totals **$17.24 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 3 |
| Represented population | 2,342,000 |
| Trainsets / vehicle modules | 483 / 1,609 |
| City infrastructure and fleet CAPEX | $4.08 B |
| Shared national factory | $669.3 M |
| Factory sizing basis | 852 modules for Kathmandu, then reused nationally |
| **Total national programme** | **$4.79 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $975.5 M (20.4%) |
| Domestic / local capital | $3.82 B (79.6%) |
| Annual external capital draw | $139.4 M / yr |
| Annual local capital draw | $545.2 M / yr |
| Annual public construction commitment | $381.9 M / yr for 7 years |
| Annual post-grace debt service | $309.5 M / yr |
| Default foreign-turnkey external capital | $8.63 B |
| External capital saved | $7.65 B |
| Capital + lifetime external interest saved | $17.24 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $2.42 B | $362.9 M | $2.06 B |
| Stations | $433.0 M | $86.6 M | $346.4 M |
| Depots | $218.5 M | $54.6 M | $163.9 M |
| Rolling stock | $463.5 M | $162.2 M | $301.3 M |
| Dedicated solar plants | $257.3 M | $115.8 M | $141.5 M |
| Residual train control | $13.2 M | $6.6 M | $6.6 M |
| Charging microgrids | $20.9 M | $8.4 M | $12.6 M |
| EPC / project services | $296.6 M | $44.5 M | $252.2 M |
| Shared national trainset factory | $669.3 M | $133.9 M | $535.5 M |
| **Total** | **$4.79 B** | **$975.5 M** | **$3.82 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Kathmandu](Kathmandu/README.md) | 1,442,000 | 213 | $2.46 B | $513.2 M | $1.95 B |
| [Pokhara](Pokhara/README.md) | 600,000 | 217 | $1.10 B | $230.9 M | $871.7 M |
| [Biratnagar](Biratnagar/README.md) | 300,000 | 53 | $508.7 M | $90.6 M | $418.1 M |

## Local Basis And Regeneration

Country finance parameters use `NP` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
