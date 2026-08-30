# Tanzania National OpenSourceRail Strategy

This page contains only Tanzania-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$16.63 B (86.1%) of external capital** and **$20.85 B of external interest**. Capital plus saved interest totals **$37.49 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 15 |
| Represented population | 13,854,689 |
| Trainsets / vehicle modules | 2,077 / 8,168 |
| City infrastructure and fleet CAPEX | $10.46 B |
| Shared national factory | $255.2 M |
| Factory sizing basis | 4,254 modules for Dar Es Salaam, then reused nationally |
| **Total national programme** | **$10.73 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $2.68 B (25.0%) |
| Domestic / local capital | $8.05 B (75.0%) |
| Annual external capital draw | $383.5 M / yr |
| Annual local capital draw | $1.15 B / yr |
| Annual public construction commitment | $962.4 M / yr for 7 years |
| Annual post-grace debt service | $801.6 M / yr |
| Default foreign-turnkey external capital | $19.32 B |
| External capital saved | $16.63 B |
| Capital + lifetime external interest saved | $37.49 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $3.70 B | $554.3 M | $3.14 B |
| Stations | $2.13 B | $425.1 M | $1.70 B |
| Depots | $120.0 M | $30.0 M | $90.0 M |
| Rolling stock | $2.33 B | $816.0 M | $1.52 B |
| Dedicated solar plants | $1.45 B | $652.1 M | $797.0 M |
| Residual train control | $57.3 M | $28.6 M | $28.6 M |
| Charging microgrids | $91.4 M | $36.6 M | $54.8 M |
| EPC / project services | $607.3 M | $91.1 M | $516.2 M |
| Shared national trainset factory | $255.2 M | $51.0 M | $204.2 M |
| **Total** | **$10.73 B** | **$2.68 B** | **$8.05 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Dar Es Salaam](Dar-Es-Salaam/README.md) | 7,404,689 | 709 | $4.62 B | $1.25 B | $3.36 B |
| [Mwanza](Mwanza/README.md) | 1,100,000 | 219 | $1.51 B | $365.0 M | $1.14 B |
| [Dodoma](Dodoma/README.md) | 800,000 | 113 | $411.0 M | $99.1 M | $311.9 M |
| [Arusha](Arusha/README.md) | 700,000 | 153 | $510.7 M | $124.9 M | $385.8 M |
| [Mbeya](Mbeya/README.md) | 550,000 | 112 | $398.7 M | $97.2 M | $301.6 M |
| [Morogoro](Morogoro/README.md) | 500,000 | 120 | $532.5 M | $126.1 M | $406.5 M |
| [Zanzibar City](Zanzibar-City/README.md) | 500,000 | 134 | $592.7 M | $141.1 M | $451.6 M |
| [Tanga](Tanga/README.md) | 400,000 | 108 | $421.0 M | $103.9 M | $317.0 M |
| [Kigoma](Kigoma/README.md) | 300,000 | 76 | $255.3 M | $58.0 M | $197.3 M |
| [Moshi](Moshi/README.md) | 300,000 | 73 | $297.8 M | $64.5 M | $233.3 M |
| [Tabora](Tabora/README.md) | 300,000 | 49 | $188.7 M | $40.1 M | $148.7 M |
| [Iringa](Iringa/README.md) | 250,000 | 58 | $211.6 M | $45.5 M | $166.1 M |
| [Shinyanga](Shinyanga/README.md) | 250,000 | 76 | $248.6 M | $54.6 M | $194.0 M |
| [Songea](Songea/README.md) | 250,000 | 37 | $129.6 M | $28.3 M | $101.3 M |
| [Sumbawanga](Sumbawanga/README.md) | 250,000 | 40 | $137.1 M | $29.6 M | $107.6 M |

## Local Basis And Regeneration

Country finance parameters use `TZ` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
