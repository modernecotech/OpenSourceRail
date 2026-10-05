# Nigeria National OpenSourceRail Strategy

This page contains only Nigeria-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$35.20 B (88.5%) of external capital** and **$44.12 B of external interest**. Capital plus saved interest totals **$79.32 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 10 |
| Represented population | 19,200,000 |
| Trainsets / vehicle modules | 2,061 / 9,547 |
| City infrastructure and fleet CAPEX | $21.36 B |
| Shared national factory | $697.0 M |
| Factory sizing basis | 4,068 modules for Kano, then reused nationally |
| **Total national programme** | **$22.11 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $4.59 B (20.8%) |
| Domestic / local capital | $17.51 B (79.2%) |
| Annual external capital draw | $656.2 M / yr |
| Annual local capital draw | $2.50 B / yr |
| Annual public construction commitment | $2.60 B / yr for 7 years |
| Annual post-grace debt service | $2.19 B / yr |
| Default foreign-turnkey external capital | $39.79 B |
| External capital saved | $35.20 B |
| Capital + lifetime external interest saved | $79.32 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $12.20 B | $1.83 B | $10.37 B |
| Stations | $2.59 B | $517.1 M | $2.07 B |
| Depots | $968.2 M | $242.1 M | $726.2 M |
| Rolling stock | $2.70 B | $944.4 M | $1.75 B |
| Dedicated solar plants | $1.39 B | $626.6 M | $765.9 M |
| Residual train control | $63.6 M | $31.8 M | $31.8 M |
| Charging microgrids | $146.8 M | $58.7 M | $88.1 M |
| EPC / project services | $1.36 B | $203.3 M | $1.15 B |
| Shared national trainset factory | $697.0 M | $139.4 M | $557.6 M |
| **Total** | **$22.11 B** | **$4.59 B** | **$17.51 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Kano](Kano/README.md) | 4,200,000 | 678 | $7.34 B | $1.58 B | $5.75 B |
| [Ibadan](Ibadan/README.md) | 3,900,000 | 182 | $1.99 B | $445.8 M | $1.55 B |
| [Port Harcourt](Port-Harcourt/README.md) | 3,000,000 | 221 | $2.75 B | $551.6 M | $2.20 B |
| [Benin City](Benin-City/README.md) | 1,800,000 | 162 | $1.74 B | $357.2 M | $1.38 B |
| [Onitsha](Onitsha/README.md) | 1,500,000 | 210 | $2.66 B | $535.0 M | $2.13 B |
| [Maiduguri](Maiduguri/README.md) | 1,200,000 | 191 | $2.54 B | $488.1 M | $2.05 B |
| [Ilorin](Ilorin/README.md) | 1,000,000 | 130 | $699.8 M | $147.7 M | $552.1 M |
| [Aba Ng](Aba-Ng/README.md) | 900,000 | 87 | $517.7 M | $107.3 M | $410.5 M |
| [Jos](Jos/README.md) | 900,000 | 117 | $646.6 M | $131.1 M | $515.5 M |
| [Uyo](Uyo/README.md) | 800,000 | 83 | $476.4 M | $99.1 M | $377.3 M |

## Local Basis And Regeneration

Country finance parameters use `NG` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
