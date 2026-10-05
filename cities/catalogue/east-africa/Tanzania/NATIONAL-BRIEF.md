# Tanzania National OpenSourceRail Strategy

This page contains only Tanzania-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$31.46 B (88.2%) of external capital** and **$39.43 B of external interest**. Capital plus saved interest totals **$70.89 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 15 |
| Represented population | 13,854,689 |
| Trainsets / vehicle modules | 2,245 / 9,009 |
| City infrastructure and fleet CAPEX | $18.82 B |
| Shared national factory | $927.4 M |
| Factory sizing basis | 4,584 modules for Dar Es Salaam, then reused nationally |
| **Total national programme** | **$19.81 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $4.20 B (21.2%) |
| Domestic / local capital | $15.61 B (78.8%) |
| Annual external capital draw | $600.0 M / yr |
| Annual local capital draw | $2.23 B / yr |
| Annual public construction commitment | $1.82 B / yr for 7 years |
| Annual post-grace debt service | $1.50 B / yr |
| Default foreign-turnkey external capital | $35.66 B |
| External capital saved | $31.46 B |
| Capital + lifetime external interest saved | $70.89 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $9.67 B | $1.45 B | $8.22 B |
| Stations | $3.00 B | $599.6 M | $2.40 B |
| Depots | $1.04 B | $258.8 M | $776.3 M |
| Rolling stock | $2.57 B | $900.4 M | $1.67 B |
| Dedicated solar plants | $1.21 B | $546.1 M | $667.4 M |
| Residual train control | $53.2 M | $26.6 M | $26.6 M |
| Charging microgrids | $127.0 M | $50.8 M | $76.2 M |
| EPC / project services | $1.22 B | $182.5 M | $1.03 B |
| Shared national trainset factory | $927.4 M | $185.5 M | $741.9 M |
| **Total** | **$19.81 B** | **$4.20 B** | **$15.61 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Dar Es Salaam](Dar-Es-Salaam/README.md) | 7,404,689 | 764 | $8.71 B | $1.95 B | $6.77 B |
| [Mwanza](Mwanza/README.md) | 1,100,000 | 314 | $3.20 B | $665.2 M | $2.54 B |
| [Dodoma](Dodoma/README.md) | 800,000 | 139 | $748.6 M | $154.7 M | $593.9 M |
| [Arusha](Arusha/README.md) | 700,000 | 168 | $874.8 M | $181.6 M | $693.2 M |
| [Mbeya](Mbeya/README.md) | 550,000 | 134 | $713.1 M | $148.6 M | $564.6 M |
| [Morogoro](Morogoro/README.md) | 500,000 | 134 | $794.5 M | $164.3 M | $630.2 M |
| [Zanzibar City](Zanzibar-City/README.md) | 500,000 | 128 | $660.1 M | $141.1 M | $519.0 M |
| [Tanga](Tanga/README.md) | 400,000 | 132 | $776.9 M | $162.2 M | $614.7 M |
| [Kigoma](Kigoma/README.md) | 300,000 | 60 | $425.7 M | $80.8 M | $344.9 M |
| [Moshi](Moshi/README.md) | 300,000 | 62 | $490.7 M | $91.6 M | $399.1 M |
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
