# South Africa National OpenSourceRail Strategy

This page contains only South Africa-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$16.13 B (87.8%) of external capital** and **$19.83 B of external interest**. Capital plus saved interest totals **$35.96 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 5 |
| Represented population | 6,200,000 |
| Trainsets / vehicle modules | 1,166 / 5,260 |
| City infrastructure and fleet CAPEX | $9.61 B |
| Shared national factory | $554.0 M |
| Factory sizing basis | 3,648 modules for Durban, then reused nationally |
| **Total national programme** | **$10.20 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $2.24 B (21.9%) |
| Domestic / local capital | $7.97 B (78.1%) |
| Annual external capital draw | $447.0 M / yr |
| Annual local capital draw | $1.59 B / yr |
| Annual public construction commitment | $1.09 B / yr for 5 years |
| Annual post-grace debt service | $818.3 M / yr |
| Default foreign-turnkey external capital | $18.37 B |
| External capital saved | $16.13 B |
| Capital + lifetime external interest saved | $35.96 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $4.89 B | $734.1 M | $4.16 B |
| Stations | $1.27 B | $253.1 M | $1.01 B |
| Depots | $481.7 M | $120.4 M | $361.2 M |
| Rolling stock | $1.50 B | $525.9 M | $976.7 M |
| Dedicated solar plants | $795.4 M | $357.9 M | $437.5 M |
| Residual train control | $27.4 M | $13.7 M | $13.7 M |
| Charging microgrids | $67.2 M | $26.9 M | $40.3 M |
| EPC / project services | $615.5 M | $92.3 M | $523.2 M |
| Shared national trainset factory | $554.0 M | $110.8 M | $443.2 M |
| **Total** | **$10.20 B** | **$2.24 B** | **$7.97 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Durban](Durban/README.md) | 3,900,000 | 608 | $6.52 B | $1.47 B | $5.05 B |
| [East London Za](East-London-Za/README.md) | 800,000 | 185 | $974.1 M | $210.8 M | $763.3 M |
| [Bloemfontein](Bloemfontein/README.md) | 600,000 | 183 | $931.3 M | $202.5 M | $728.7 M |
| [Polokwane](Polokwane/README.md) | 600,000 | 128 | $690.1 M | $142.7 M | $547.4 M |
| [Nelspruit](Nelspruit/README.md) | 300,000 | 62 | $493.2 M | $91.3 M | $401.9 M |

## Local Basis And Regeneration

Country finance parameters use `ZA` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
