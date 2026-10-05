# South Africa National OpenSourceRail Strategy

This page contains only South Africa-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$31.35 B (89.7%) of external capital** and **$38.55 B of external interest**. Capital plus saved interest totals **$69.90 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 5 |
| Represented population | 6,200,000 |
| Trainsets / vehicle modules | 1,166 / 5,260 |
| City infrastructure and fleet CAPEX | $18.84 B |
| Shared national factory | $554.0 M |
| Factory sizing basis | 3,648 modules for Durban, then reused nationally |
| **Total national programme** | **$19.43 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $3.62 B (18.6%) |
| Domestic / local capital | $15.81 B (81.4%) |
| Annual external capital draw | $723.8 M / yr |
| Annual local capital draw | $3.16 B / yr |
| Annual public construction commitment | $2.12 B / yr for 5 years |
| Annual post-grace debt service | $1.58 B / yr |
| Default foreign-turnkey external capital | $34.97 B |
| External capital saved | $31.35 B |
| Capital + lifetime external interest saved | $69.90 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $13.52 B | $2.03 B | $11.49 B |
| Stations | $1.27 B | $253.1 M | $1.01 B |
| Depots | $481.7 M | $120.4 M | $361.2 M |
| Rolling stock | $1.50 B | $525.9 M | $976.7 M |
| Dedicated solar plants | $795.4 M | $357.9 M | $437.5 M |
| Residual train control | $27.4 M | $13.7 M | $13.7 M |
| Charging microgrids | $67.2 M | $26.9 M | $40.3 M |
| EPC / project services | $1.22 B | $182.8 M | $1.04 B |
| Shared national trainset factory | $554.0 M | $110.8 M | $443.2 M |
| **Total** | **$19.43 B** | **$3.62 B** | **$15.81 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Durban](Durban/README.md) | 3,900,000 | 608 | $15.71 B | $2.85 B | $12.86 B |
| [East London Za](East-London-Za/README.md) | 800,000 | 185 | $1.01 B | $216.6 M | $796.1 M |
| [Bloemfontein](Bloemfontein/README.md) | 600,000 | 183 | $931.4 M | $202.6 M | $728.8 M |
| [Polokwane](Polokwane/README.md) | 600,000 | 128 | $690.2 M | $142.7 M | $547.6 M |
| [Nelspruit](Nelspruit/README.md) | 300,000 | 62 | $493.2 M | $91.3 M | $401.9 M |

## Local Basis And Regeneration

Country finance parameters use `ZA` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
