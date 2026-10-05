# Tanzania National OpenSourceRail Strategy

This page contains only Tanzania-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$115.53 B (90.7%) of external capital** and **$144.82 B of external interest**. Capital plus saved interest totals **$260.35 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 15 |
| Represented population | 13,854,689 |
| Trainsets / vehicle modules | 2,245 / 9,009 |
| City infrastructure and fleet CAPEX | $69.77 B |
| Shared national factory | $927.4 M |
| Factory sizing basis | 4,584 modules for Dar Es Salaam, then reused nationally |
| **Total national programme** | **$70.76 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $11.84 B (16.7%) |
| Domestic / local capital | $58.92 B (83.3%) |
| Annual external capital draw | $1.69 B / yr |
| Annual local capital draw | $8.42 B / yr |
| Annual public construction commitment | $6.69 B / yr for 7 years |
| Annual post-grace debt service | $5.41 B / yr |
| Default foreign-turnkey external capital | $127.37 B |
| External capital saved | $115.53 B |
| Capital + lifetime external interest saved | $260.35 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $57.29 B | $8.59 B | $48.69 B |
| Stations | $3.00 B | $599.6 M | $2.40 B |
| Depots | $1.04 B | $258.8 M | $776.3 M |
| Rolling stock | $2.57 B | $900.4 M | $1.67 B |
| Dedicated solar plants | $1.21 B | $546.1 M | $667.4 M |
| Residual train control | $53.2 M | $26.6 M | $26.6 M |
| Charging microgrids | $127.0 M | $50.8 M | $76.2 M |
| EPC / project services | $4.55 B | $682.5 M | $3.87 B |
| Shared national trainset factory | $927.4 M | $185.5 M | $741.9 M |
| **Total** | **$70.76 B** | **$11.84 B** | **$58.92 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Dar Es Salaam](Dar-Es-Salaam/README.md) | 7,404,689 | 764 | $37.59 B | $6.28 B | $31.31 B |
| [Mwanza](Mwanza/README.md) | 1,100,000 | 314 | $20.55 B | $3.27 B | $17.29 B |
| [Dodoma](Dodoma/README.md) | 800,000 | 139 | $748.6 M | $154.7 M | $593.9 M |
| [Arusha](Arusha/README.md) | 700,000 | 168 | $877.1 M | $181.9 M | $695.2 M |
| [Mbeya](Mbeya/README.md) | 550,000 | 134 | $718.9 M | $149.4 M | $569.5 M |
| [Morogoro](Morogoro/README.md) | 500,000 | 134 | $794.5 M | $164.3 M | $630.2 M |
| [Zanzibar City](Zanzibar-City/README.md) | 500,000 | 128 | $2.07 B | $353.1 M | $1.72 B |
| [Tanga](Tanga/README.md) | 400,000 | 132 | $4.03 B | $650.4 M | $3.38 B |
| [Kigoma](Kigoma/README.md) | 300,000 | 60 | $425.7 M | $80.8 M | $344.9 M |
| [Moshi](Moshi/README.md) | 300,000 | 62 | $541.4 M | $99.2 M | $442.2 M |
| [Tabora](Tabora/README.md) | 300,000 | 42 | $271.2 M | $52.2 M | $219.0 M |
| [Iringa](Iringa/README.md) | 250,000 | 48 | $368.0 M | $68.6 M | $299.4 M |
| [Shinyanga](Shinyanga/README.md) | 250,000 | 60 | $392.1 M | $73.3 M | $318.8 M |
| [Songea](Songea/README.md) | 250,000 | 29 | $171.7 M | $33.4 M | $138.3 M |
| [Sumbawanga](Sumbawanga/README.md) | 250,000 | 31 | $210.6 M | $41.5 M | $169.1 M |

## Local Basis And Regeneration

Country finance parameters use `TZ` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
