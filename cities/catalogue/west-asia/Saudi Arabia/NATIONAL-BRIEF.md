# Saudi Arabia National OpenSourceRail Strategy

This page contains only Saudi Arabia-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$37.71 B (88.4%) of external capital** and **$46.36 B of external interest**. Capital plus saved interest totals **$84.08 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 14 |
| Represented population | 15,600,000 |
| Trainsets / vehicle modules | 3,016 / 11,356 |
| City infrastructure and fleet CAPEX | $22.85 B |
| Shared national factory | $783.8 M |
| Factory sizing basis | 3,090 modules for Jeddah, then reused nationally |
| **Total national programme** | **$23.69 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $4.93 B (20.8%) |
| Domestic / local capital | $18.76 B (79.2%) |
| Annual external capital draw | $986.4 M / yr |
| Annual local capital draw | $3.75 B / yr |
| Annual public construction commitment | $1.65 B / yr for 5 years |
| Annual post-grace debt service | $1.14 B / yr |
| Default foreign-turnkey external capital | $42.64 B |
| External capital saved | $37.71 B |
| Capital + lifetime external interest saved | $84.08 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $13.22 B | $1.98 B | $11.24 B |
| Stations | $2.23 B | $445.3 M | $1.78 B |
| Depots | $1.20 B | $300.2 M | $900.6 M |
| Rolling stock | $3.28 B | $1.15 B | $2.13 B |
| Dedicated solar plants | $1.31 B | $590.6 M | $721.8 M |
| Residual train control | $75.5 M | $37.7 M | $37.7 M |
| Charging microgrids | $123.0 M | $49.2 M | $73.8 M |
| EPC / project services | $1.46 B | $219.6 M | $1.24 B |
| Shared national trainset factory | $783.8 M | $156.8 M | $627.1 M |
| **Total** | **$23.69 B** | **$4.93 B** | **$18.76 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Jeddah](Jeddah/README.md) | 4,700,000 | 515 | $5.37 B | $1.19 B | $4.18 B |
| [Mecca](Mecca/README.md) | 2,200,000 | 252 | $2.86 B | $570.5 M | $2.29 B |
| [Dammam](Dammam/README.md) | 1,500,000 | 300 | $3.27 B | $662.0 M | $2.61 B |
| [Medina](Medina/README.md) | 1,500,000 | 211 | $2.53 B | $499.6 M | $2.03 B |
| [Hofuf](Hofuf/README.md) | 800,000 | 212 | $957.2 M | $207.3 M | $749.9 M |
| [Buraidah](Buraidah/README.md) | 700,000 | 172 | $870.3 M | $183.0 M | $687.2 M |
| [Taif](Taif/README.md) | 700,000 | 168 | $854.9 M | $178.5 M | $676.5 M |
| [Tabuk](Tabuk/README.md) | 650,000 | 173 | $893.5 M | $186.4 M | $707.1 M |
| [Khamis Mushait](Khamis-Mushait/README.md) | 600,000 | 215 | $1.05 B | $222.1 M | $824.8 M |
| [Hail](Hail/README.md) | 500,000 | 171 | $841.1 M | $177.7 M | $663.4 M |
| [Najran](Najran/README.md) | 500,000 | 158 | $981.8 M | $195.3 M | $786.5 M |
| [Abha](Abha/README.md) | 450,000 | 156 | $783.5 M | $163.7 M | $619.8 M |
| [Al Kharj](Al-Kharj/README.md) | 400,000 | 176 | $860.2 M | $182.5 M | $677.7 M |
| [Jizan](Jizan/README.md) | 400,000 | 137 | $725.0 M | $151.8 M | $573.2 M |

## Local Basis And Regeneration

Country finance parameters use `SA` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
