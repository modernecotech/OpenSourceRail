# Nepal National OpenSourceRail Strategy

This page contains only Nepal-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$8.21 B (88.7%) of external capital** and **$10.29 B of external interest**. Capital plus saved interest totals **$18.50 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 3 |
| Represented population | 2,342,000 |
| Trainsets / vehicle modules | 522 / 1,744 |
| City infrastructure and fleet CAPEX | $4.36 B |
| Shared national factory | $733.0 M |
| Factory sizing basis | 932 modules for Kathmandu, then reused nationally |
| **Total national programme** | **$5.14 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.05 B (20.4%) |
| Domestic / local capital | $4.09 B (79.6%) |
| Annual external capital draw | $150.1 M / yr |
| Annual local capital draw | $584.8 M / yr |
| Annual public construction commitment | $409.8 M / yr for 7 years |
| Annual post-grace debt service | $332.2 M / yr |
| Default foreign-turnkey external capital | $9.26 B |
| External capital saved | $8.21 B |
| Capital + lifetime external interest saved | $18.50 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $2.45 B | $367.3 M | $2.08 B |
| Stations | $618.1 M | $123.6 M | $494.5 M |
| Depots | $225.1 M | $56.3 M | $168.8 M |
| Rolling stock | $502.4 M | $175.8 M | $326.5 M |
| Dedicated solar plants | $259.1 M | $116.6 M | $142.5 M |
| Residual train control | $13.5 M | $6.7 M | $6.7 M |
| Charging microgrids | $24.6 M | $9.8 M | $14.8 M |
| EPC / project services | $319.6 M | $47.9 M | $271.6 M |
| Shared national trainset factory | $733.0 M | $146.6 M | $586.4 M |
| **Total** | **$5.14 B** | **$1.05 B** | **$4.09 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Kathmandu](Kathmandu/README.md) | 1,442,000 | 233 | $2.62 B | $547.9 M | $2.07 B |
| [Pokhara](Pokhara/README.md) | 600,000 | 234 | $1.23 B | $256.4 M | $968.8 M |
| [Biratnagar](Biratnagar/README.md) | 300,000 | 55 | $515.9 M | $92.1 M | $423.7 M |

## Local Basis And Regeneration

Country finance parameters use `NP` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
