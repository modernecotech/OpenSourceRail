# Angola National OpenSourceRail Strategy

This page contains only Angola-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$17.42 B (88.0%) of external capital** and **$21.42 B of external interest**. Capital plus saved interest totals **$38.84 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 9 |
| Represented population | 13,135,000 |
| Trainsets / vehicle modules | 1,321 / 5,642 |
| City infrastructure and fleet CAPEX | $10.51 B |
| Shared national factory | $460.7 M |
| Factory sizing basis | 3,606 modules for Luanda, then reused nationally |
| **Total national programme** | **$11.00 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $2.38 B (21.7%) |
| Domestic / local capital | $8.62 B (78.3%) |
| Annual external capital draw | $476.9 M / yr |
| Annual local capital draw | $1.72 B / yr |
| Annual public construction commitment | $1.25 B / yr for 5 years |
| Annual post-grace debt service | $947.5 M / yr |
| Default foreign-turnkey external capital | $19.81 B |
| External capital saved | $17.42 B |
| Capital + lifetime external interest saved | $38.84 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $5.38 B | $806.6 M | $4.57 B |
| Stations | $1.41 B | $282.3 M | $1.13 B |
| Depots | $605.8 M | $151.5 M | $454.4 M |
| Rolling stock | $1.62 B | $565.4 M | $1.05 B |
| Dedicated solar plants | $762.2 M | $343.0 M | $419.2 M |
| Residual train control | $30.2 M | $15.1 M | $15.1 M |
| Charging microgrids | $70.3 M | $28.1 M | $42.2 M |
| EPC / project services | $670.0 M | $100.5 M | $569.5 M |
| Shared national trainset factory | $460.7 M | $92.1 M | $368.6 M |
| **Total** | **$11.00 B** | **$2.38 B** | **$8.62 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Luanda](Luanda/README.md) | 9,085,000 | 601 | $6.34 B | $1.44 B | $4.89 B |
| [Huambo](Huambo/README.md) | 800,000 | 136 | $735.2 M | $150.9 M | $584.3 M |
| [Lubango](Lubango/README.md) | 700,000 | 138 | $764.3 M | $156.3 M | $608.0 M |
| [Benguela](Benguela/README.md) | 600,000 | 151 | $770.3 M | $161.3 M | $609.1 M |
| [Lobito](Lobito/README.md) | 500,000 | 98 | $575.5 M | $117.2 M | $458.3 M |
| [Malanje](Malanje/README.md) | 500,000 | 49 | $286.2 M | $59.2 M | $227.1 M |
| [Uige](Uige/README.md) | 400,000 | 24 | $129.2 M | $26.9 M | $102.2 M |
| [Namibe](Namibe/README.md) | 300,000 | 76 | $536.2 M | $99.6 M | $436.6 M |
| [Soyo](Soyo/README.md) | 250,000 | 48 | $377.9 M | $72.1 M | $305.8 M |

## Local Basis And Regeneration

Country finance parameters use `AO` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
