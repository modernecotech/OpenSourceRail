# Sudan National OpenSourceRail Strategy

This page contains only Sudan-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$19.98 B (88.4%) of external capital** and **$25.81 B of external interest**. Capital plus saved interest totals **$45.79 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 7 |
| Represented population | 11,029,000 |
| Trainsets / vehicle modules | 1,241 / 5,584 |
| City infrastructure and fleet CAPEX | $11.65 B |
| Shared national factory | $841.3 M |
| Factory sizing basis | 3,252 modules for Khartoum, then reused nationally |
| **Total national programme** | **$12.55 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $2.61 B (20.8%) |
| Domestic / local capital | $9.94 B (79.2%) |
| Annual external capital draw | $261.1 M / yr |
| Annual local capital draw | $994.0 M / yr |
| Annual public construction commitment | $1.51 B / yr for 10 years |
| Annual post-grace debt service | $1.37 B / yr |
| Default foreign-turnkey external capital | $22.59 B |
| External capital saved | $19.98 B |
| Capital + lifetime external interest saved | $45.79 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $6.78 B | $1.02 B | $5.76 B |
| Stations | $1.12 B | $225.0 M | $899.8 M |
| Depots | $603.3 M | $150.8 M | $452.5 M |
| Rolling stock | $1.59 B | $555.5 M | $1.03 B |
| Dedicated solar plants | $739.3 M | $332.7 M | $406.6 M |
| Residual train control | $35.9 M | $18.0 M | $18.0 M |
| Charging microgrids | $72.0 M | $28.8 M | $43.2 M |
| EPC / project services | $772.8 M | $115.9 M | $656.8 M |
| Shared national trainset factory | $841.3 M | $168.3 M | $673.0 M |
| **Total** | **$12.55 B** | **$2.61 B** | **$9.94 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Khartoum](Khartoum/README.md) | 5,829,000 | 542 | $6.02 B | $1.31 B | $4.71 B |
| [Omdurman](Omdurman/README.md) | 2,800,000 | 271 | $3.12 B | $623.8 M | $2.50 B |
| [Nyala](Nyala/README.md) | 600,000 | 123 | $703.3 M | $142.8 M | $560.5 M |
| [El Obeid](El-Obeid/README.md) | 500,000 | 121 | $657.3 M | $134.7 M | $522.6 M |
| [Kassala](Kassala/README.md) | 500,000 | 66 | $447.5 M | $87.8 M | $359.7 M |
| [Port Sudan](Port-Sudan/README.md) | 500,000 | 82 | $454.1 M | $92.6 M | $361.5 M |
| [Waw](Waw/README.md) | 300,000 | 36 | $246.2 M | $47.0 M | $199.3 M |

## Local Basis And Regeneration

Country finance parameters use `SD` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
