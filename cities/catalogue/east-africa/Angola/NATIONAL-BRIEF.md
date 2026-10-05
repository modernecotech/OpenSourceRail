# Angola National OpenSourceRail Strategy

This page contains only Angola-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$40.55 B (90.0%) of external capital** and **$49.85 B of external interest**. Capital plus saved interest totals **$90.39 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 9 |
| Represented population | 13,135,000 |
| Trainsets / vehicle modules | 1,321 / 5,642 |
| City infrastructure and fleet CAPEX | $24.52 B |
| Shared national factory | $460.7 M |
| Factory sizing basis | 3,606 modules for Luanda, then reused nationally |
| **Total national programme** | **$25.02 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $4.49 B (17.9%) |
| Domestic / local capital | $20.53 B (82.1%) |
| Annual external capital draw | $897.4 M / yr |
| Annual local capital draw | $4.11 B / yr |
| Annual public construction commitment | $2.91 B / yr for 5 years |
| Annual post-grace debt service | $2.19 B / yr |
| Default foreign-turnkey external capital | $45.03 B |
| External capital saved | $40.55 B |
| Capital + lifetime external interest saved | $90.39 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $18.47 B | $2.77 B | $15.70 B |
| Stations | $1.41 B | $282.3 M | $1.13 B |
| Depots | $605.8 M | $151.5 M | $454.4 M |
| Rolling stock | $1.62 B | $565.4 M | $1.05 B |
| Dedicated solar plants | $762.2 M | $343.0 M | $419.2 M |
| Residual train control | $30.2 M | $15.1 M | $15.1 M |
| Charging microgrids | $70.3 M | $28.1 M | $42.2 M |
| EPC / project services | $1.59 B | $238.0 M | $1.35 B |
| Shared national trainset factory | $460.7 M | $92.1 M | $368.6 M |
| **Total** | **$25.02 B** | **$4.49 B** | **$20.53 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Luanda](Luanda/README.md) | 9,085,000 | 601 | $12.35 B | $2.35 B | $10.00 B |
| [Huambo](Huambo/README.md) | 800,000 | 136 | $735.2 M | $150.9 M | $584.3 M |
| [Lubango](Lubango/README.md) | 700,000 | 138 | $764.5 M | $156.4 M | $608.1 M |
| [Benguela](Benguela/README.md) | 600,000 | 151 | $1.02 B | $198.7 M | $821.1 M |
| [Lobito](Lobito/README.md) | 500,000 | 98 | $5.44 B | $846.7 M | $4.59 B |
| [Malanje](Malanje/README.md) | 500,000 | 49 | $286.2 M | $59.2 M | $227.1 M |
| [Uige](Uige/README.md) | 400,000 | 24 | $129.2 M | $26.9 M | $102.2 M |
| [Namibe](Namibe/README.md) | 300,000 | 76 | $3.43 B | $533.3 M | $2.89 B |
| [Soyo](Soyo/README.md) | 250,000 | 48 | $377.9 M | $72.1 M | $305.8 M |

## Local Basis And Regeneration

Country finance parameters use `AO` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
