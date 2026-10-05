# Afghanistan National OpenSourceRail Strategy

This page contains only Afghanistan-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$12.47 B (88.4%) of external capital** and **$16.11 B of external interest**. Capital plus saved interest totals **$28.58 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 5 |
| Represented population | 7,051,000 |
| Trainsets / vehicle modules | 881 / 3,603 |
| City infrastructure and fleet CAPEX | $6.75 B |
| Shared national factory | $1.02 B |
| Factory sizing basis | 1,920 modules for Kabul, then reused nationally |
| **Total national programme** | **$7.84 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.63 B (20.9%) |
| Domestic / local capital | $6.20 B (79.1%) |
| Annual external capital draw | $163.4 M / yr |
| Annual local capital draw | $620.2 M / yr |
| Annual public construction commitment | $1.09 B / yr for 10 years |
| Annual post-grace debt service | $999.6 M / yr |
| Default foreign-turnkey external capital | $14.10 B |
| External capital saved | $12.47 B |
| Capital + lifetime external interest saved | $28.58 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $3.66 B | $548.6 M | $3.11 B |
| Stations | $841.5 M | $168.3 M | $673.2 M |
| Depots | $386.3 M | $96.6 M | $289.7 M |
| Rolling stock | $1.04 B | $364.9 M | $677.6 M |
| Dedicated solar plants | $340.2 M | $153.1 M | $187.1 M |
| Residual train control | $18.8 M | $9.4 M | $9.4 M |
| Charging microgrids | $41.0 M | $16.4 M | $24.6 M |
| EPC / project services | $490.4 M | $73.6 M | $416.8 M |
| Shared national trainset factory | $1.02 B | $203.6 M | $814.5 M |
| **Total** | **$7.84 B** | **$1.63 B** | **$6.20 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Kabul](Kabul/README.md) | 4,601,000 | 320 | $3.54 B | $766.5 M | $2.78 B |
| [Herat](Herat/README.md) | 800,000 | 124 | $661.0 M | $137.3 M | $523.7 M |
| [Kandahar](Kandahar/README.md) | 700,000 | 130 | $823.2 M | $163.8 M | $659.5 M |
| [Mazar E Sharif](Mazar-E-Sharif/README.md) | 600,000 | 177 | $999.3 M | $204.4 M | $794.9 M |
| [Jalalabad Af](Jalalabad-Af/README.md) | 350,000 | 130 | $719.7 M | $148.0 M | $571.7 M |

## Local Basis And Regeneration

Country finance parameters use `AF` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
