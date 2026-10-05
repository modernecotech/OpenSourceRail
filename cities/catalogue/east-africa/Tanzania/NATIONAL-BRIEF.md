# Tanzania National OpenSourceRail Strategy

This page contains only Tanzania-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$24.94 B (88.2%) of external capital** and **$31.26 B of external interest**. Capital plus saved interest totals **$56.19 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 15 |
| Represented population | 13,854,689 |
| Trainsets / vehicle modules | 1,962 / 7,552 |
| City infrastructure and fleet CAPEX | $15.05 B |
| Shared national factory | $609.6 M |
| Factory sizing basis | 3,606 modules for Dar Es Salaam, then reused nationally |
| **Total national programme** | **$15.71 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $3.34 B (21.2%) |
| Domestic / local capital | $12.37 B (78.8%) |
| Annual external capital draw | $476.6 M / yr |
| Annual local capital draw | $1.77 B / yr |
| Annual public construction commitment | $1.44 B / yr for 7 years |
| Annual post-grace debt service | $1.19 B / yr |
| Default foreign-turnkey external capital | $28.27 B |
| External capital saved | $24.94 B |
| Capital + lifetime external interest saved | $56.19 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $8.39 B | $1.26 B | $7.14 B |
| Stations | $1.44 B | $288.6 M | $1.15 B |
| Depots | $973.3 M | $243.3 M | $730.0 M |
| Rolling stock | $2.17 B | $757.8 M | $1.41 B |
| Dedicated solar plants | $1.05 B | $470.3 M | $574.9 M |
| Residual train control | $46.8 M | $23.4 M | $23.4 M |
| Charging microgrids | $70.1 M | $28.0 M | $42.1 M |
| EPC / project services | $959.2 M | $143.9 M | $815.3 M |
| Shared national trainset factory | $609.6 M | $121.9 M | $487.7 M |
| **Total** | **$15.71 B** | **$3.34 B** | **$12.37 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Dar Es Salaam](Dar-Es-Salaam/README.md) | 7,404,689 | 601 | $6.19 B | $1.41 B | $4.78 B |
| [Mwanza](Mwanza/README.md) | 1,100,000 | 191 | $2.21 B | $450.3 M | $1.76 B |
| [Dodoma](Dodoma/README.md) | 800,000 | 137 | $734.4 M | $151.8 M | $582.6 M |
| [Arusha](Arusha/README.md) | 700,000 | 169 | $855.7 M | $178.1 M | $677.6 M |
| [Mbeya](Mbeya/README.md) | 550,000 | 130 | $644.0 M | $134.6 M | $509.4 M |
| [Morogoro](Morogoro/README.md) | 500,000 | 136 | $765.3 M | $158.8 M | $606.4 M |
| [Zanzibar City](Zanzibar-City/README.md) | 500,000 | 150 | $761.1 M | $163.4 M | $597.7 M |
| [Tanga](Tanga/README.md) | 400,000 | 120 | $680.6 M | $141.6 M | $539.1 M |
| [Kigoma](Kigoma/README.md) | 300,000 | 60 | $401.8 M | $76.2 M | $325.6 M |
| [Moshi](Moshi/README.md) | 300,000 | 61 | $445.5 M | $83.2 M | $362.3 M |
| [Tabora](Tabora/README.md) | 300,000 | 42 | $271.2 M | $52.2 M | $219.0 M |
| [Iringa](Iringa/README.md) | 250,000 | 46 | $352.2 M | $65.3 M | $286.8 M |
| [Shinyanga](Shinyanga/README.md) | 250,000 | 60 | $375.3 M | $70.1 M | $305.3 M |
| [Songea](Songea/README.md) | 250,000 | 28 | $162.4 M | $31.5 M | $131.0 M |
| [Sumbawanga](Sumbawanga/README.md) | 250,000 | 31 | $204.8 M | $40.3 M | $164.4 M |

## Local Basis And Regeneration

Country finance parameters use `TZ` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
