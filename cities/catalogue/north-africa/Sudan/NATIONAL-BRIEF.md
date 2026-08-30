# Sudan National OpenSourceRail Strategy

This page contains only Sudan-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$12.53 B (86.3%) of external capital** and **$16.18 B of external interest**. Capital plus saved interest totals **$28.71 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 7 |
| Represented population | 11,029,000 |
| Trainsets / vehicle modules | 1,319 / 6,139 |
| City infrastructure and fleet CAPEX | $7.82 B |
| Shared national factory | $229.3 M |
| Factory sizing basis | 3,822 modules for Khartoum, then reused nationally |
| **Total national programme** | **$8.06 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.99 B (24.6%) |
| Domestic / local capital | $6.08 B (75.4%) |
| Annual external capital draw | $198.7 M / yr |
| Annual local capital draw | $607.6 M / yr |
| Annual public construction commitment | $940.1 M / yr for 10 years |
| Annual post-grace debt service | $862.3 M / yr |
| Default foreign-turnkey external capital | $14.51 B |
| External capital saved | $12.53 B |
| Capital + lifetime external interest saved | $28.71 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $2.87 B | $429.9 M | $2.44 B |
| Stations | $1.59 B | $318.5 M | $1.27 B |
| Depots | $56.0 M | $14.0 M | $42.0 M |
| Rolling stock | $1.74 B | $608.5 M | $1.13 B |
| Dedicated solar plants | $984.7 M | $443.1 M | $541.6 M |
| Residual train control | $42.1 M | $21.1 M | $21.1 M |
| Charging microgrids | $90.4 M | $36.2 M | $54.3 M |
| EPC / project services | $463.1 M | $69.5 M | $393.6 M |
| Shared national trainset factory | $229.3 M | $45.9 M | $183.5 M |
| **Total** | **$8.06 B** | **$1.99 B** | **$6.08 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Khartoum](Khartoum/README.md) | 5,829,000 | 637 | $4.11 B | $1.08 B | $3.03 B |
| [Omdurman](Omdurman/README.md) | 2,800,000 | 312 | $2.14 B | $500.7 M | $1.64 B |
| [Nyala](Nyala/README.md) | 600,000 | 99 | $426.9 M | $98.0 M | $329.0 M |
| [El Obeid](El-Obeid/README.md) | 500,000 | 102 | $385.0 M | $92.4 M | $292.6 M |
| [Kassala](Kassala/README.md) | 500,000 | 52 | $274.4 M | $59.0 M | $215.4 M |
| [Port Sudan](Port-Sudan/README.md) | 500,000 | 76 | $320.9 M | $75.0 M | $245.9 M |
| [Waw](Waw/README.md) | 300,000 | 41 | $156.1 M | $33.0 M | $123.1 M |

## Local Basis And Regeneration

Country finance parameters use `SD` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
