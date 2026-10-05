# Morocco National OpenSourceRail Strategy

This page contains only Morocco-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$20.76 B (88.8%) of external capital** and **$25.52 B of external interest**. Capital plus saved interest totals **$46.28 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 12 |
| Represented population | 8,050,000 |
| Trainsets / vehicle modules | 1,554 / 5,062 |
| City infrastructure and fleet CAPEX | $12.14 B |
| Shared national factory | $794.6 M |
| Factory sizing basis | 1,032 modules for Marrakech, then reused nationally |
| **Total national programme** | **$12.99 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $2.62 B (20.2%) |
| Domestic / local capital | $10.37 B (79.8%) |
| Annual external capital draw | $523.4 M / yr |
| Annual local capital draw | $2.07 B / yr |
| Annual public construction commitment | $905.9 M / yr for 5 years |
| Annual post-grace debt service | $625.0 M / yr |
| Default foreign-turnkey external capital | $23.38 B |
| External capital saved | $20.76 B |
| Capital + lifetime external interest saved | $46.28 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $6.90 B | $1.04 B | $5.87 B |
| Stations | $1.67 B | $333.5 M | $1.33 B |
| Depots | $737.2 M | $184.3 M | $552.9 M |
| Rolling stock | $1.47 B | $513.6 M | $953.9 M |
| Dedicated solar plants | $497.9 M | $224.1 M | $273.9 M |
| Residual train control | $37.9 M | $19.0 M | $19.0 M |
| Charging microgrids | $64.5 M | $25.8 M | $38.7 M |
| EPC / project services | $817.1 M | $122.6 M | $694.5 M |
| Shared national trainset factory | $794.6 M | $158.9 M | $635.7 M |
| **Total** | **$12.99 B** | **$2.62 B** | **$10.37 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Fez](Fez/README.md) | 1,300,000 | 115 | $1.49 B | $292.3 M | $1.20 B |
| [Marrakech](Marrakech/README.md) | 1,200,000 | 258 | $2.86 B | $574.7 M | $2.29 B |
| [Tangier](Tangier/README.md) | 1,200,000 | 186 | $2.22 B | $443.4 M | $1.78 B |
| [Agadir](Agadir/README.md) | 900,000 | 225 | $1.07 B | $228.9 M | $839.0 M |
| [Meknes](Meknes/README.md) | 700,000 | 93 | $537.1 M | $110.4 M | $426.7 M |
| [Oujda](Oujda/README.md) | 600,000 | 89 | $515.8 M | $105.4 M | $410.4 M |
| [Kenitra](Kenitra/README.md) | 500,000 | 163 | $829.0 M | $175.6 M | $653.3 M |
| [Tetouan](Tetouan/README.md) | 500,000 | 151 | $912.8 M | $185.2 M | $727.6 M |
| [Safi](Safi/README.md) | 350,000 | 115 | $599.2 M | $125.9 M | $473.3 M |
| [Beni Mellal](Beni-Mellal/README.md) | 300,000 | 58 | $402.5 M | $76.2 M | $326.3 M |
| [Khouribga](Khouribga/README.md) | 250,000 | 39 | $278.9 M | $53.0 M | $225.9 M |
| [Nador](Nador/README.md) | 250,000 | 62 | $418.1 M | $78.9 M | $339.1 M |

## Local Basis And Regeneration

Country finance parameters use `MA` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
