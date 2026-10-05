# Angola National OpenSourceRail Strategy

This page contains only Angola-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$16.00 B (88.0%) of external capital** and **$19.68 B of external interest**. Capital plus saved interest totals **$35.68 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 9 |
| Represented population | 13,135,000 |
| Trainsets / vehicle modules | 1,248 / 5,285 |
| City infrastructure and fleet CAPEX | $9.62 B |
| Shared national factory | $453.5 M |
| Factory sizing basis | 3,318 modules for Luanda, then reused nationally |
| **Total national programme** | **$10.11 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $2.19 B (21.7%) |
| Domestic / local capital | $7.92 B (78.3%) |
| Annual external capital draw | $438.2 M / yr |
| Annual local capital draw | $1.58 B / yr |
| Annual public construction commitment | $1.14 B / yr for 5 years |
| Annual post-grace debt service | $870.4 M / yr |
| Default foreign-turnkey external capital | $18.20 B |
| External capital saved | $16.00 B |
| Capital + lifetime external interest saved | $35.68 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $5.19 B | $778.5 M | $4.41 B |
| Stations | $930.9 M | $186.2 M | $744.7 M |
| Depots | $590.4 M | $147.6 M | $442.8 M |
| Rolling stock | $1.51 B | $530.0 M | $984.4 M |
| Dedicated solar plants | $730.9 M | $328.9 M | $402.0 M |
| Residual train control | $29.0 M | $14.5 M | $14.5 M |
| Charging microgrids | $56.2 M | $22.5 M | $33.7 M |
| EPC / project services | $613.5 M | $92.0 M | $521.5 M |
| Shared national trainset factory | $453.5 M | $90.7 M | $362.8 M |
| **Total** | **$10.11 B** | **$2.19 B** | **$7.92 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Luanda](Luanda/README.md) | 9,085,000 | 553 | $5.72 B | $1.31 B | $4.41 B |
| [Huambo](Huambo/README.md) | 800,000 | 136 | $709.8 M | $146.0 M | $563.8 M |
| [Lubango](Lubango/README.md) | 700,000 | 141 | $761.5 M | $155.9 M | $605.6 M |
| [Benguela](Benguela/README.md) | 600,000 | 146 | $725.2 M | $151.9 M | $573.2 M |
| [Lobito](Lobito/README.md) | 500,000 | 86 | $470.2 M | $96.0 M | $374.2 M |
| [Malanje](Malanje/README.md) | 500,000 | 44 | $250.1 M | $51.5 M | $198.6 M |
| [Uige](Uige/README.md) | 400,000 | 24 | $129.2 M | $26.9 M | $102.2 M |
| [Namibe](Namibe/README.md) | 300,000 | 72 | $475.7 M | $88.4 M | $387.3 M |
| [Soyo](Soyo/README.md) | 250,000 | 46 | $381.0 M | $72.7 M | $308.3 M |

## Local Basis And Regeneration

Country finance parameters use `AO` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
