# Morocco National OpenSourceRail Strategy

This page contains only Morocco-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$19.62 B (88.9%) of external capital** and **$24.13 B of external interest**. Capital plus saved interest totals **$43.75 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 12 |
| Represented population | 8,050,000 |
| Trainsets / vehicle modules | 1,472 / 4,762 |
| City infrastructure and fleet CAPEX | $11.51 B |
| Shared national factory | $709.5 M |
| Factory sizing basis | 912 modules for Marrakech, then reused nationally |
| **Total national programme** | **$12.26 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $2.45 B (20.0%) |
| Domestic / local capital | $9.81 B (80.0%) |
| Annual external capital draw | $490.7 M / yr |
| Annual local capital draw | $1.96 B / yr |
| Annual public construction commitment | $856.0 M / yr for 5 years |
| Annual post-grace debt service | $590.0 M / yr |
| Default foreign-turnkey external capital | $22.08 B |
| External capital saved | $19.62 B |
| Capital + lifetime external interest saved | $43.75 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $6.94 B | $1.04 B | $5.90 B |
| Stations | $1.16 B | $232.9 M | $931.6 M |
| Depots | $722.0 M | $180.5 M | $541.5 M |
| Rolling stock | $1.38 B | $483.8 M | $898.4 M |
| Dedicated solar plants | $485.4 M | $218.4 M | $267.0 M |
| Residual train control | $36.7 M | $18.3 M | $18.3 M |
| Charging microgrids | $52.0 M | $20.8 M | $31.2 M |
| EPC / project services | $770.6 M | $115.6 M | $655.0 M |
| Shared national trainset factory | $709.5 M | $141.9 M | $567.6 M |
| **Total** | **$12.26 B** | **$2.45 B** | **$9.81 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Fez](Fez/README.md) | 1,300,000 | 109 | $1.44 B | $281.0 M | $1.15 B |
| [Marrakech](Marrakech/README.md) | 1,200,000 | 228 | $2.76 B | $538.3 M | $2.22 B |
| [Tangier](Tangier/README.md) | 1,200,000 | 165 | $1.99 B | $393.8 M | $1.59 B |
| [Agadir](Agadir/README.md) | 900,000 | 215 | $1.01 B | $217.4 M | $796.1 M |
| [Meknes](Meknes/README.md) | 700,000 | 93 | $522.8 M | $107.7 M | $415.1 M |
| [Oujda](Oujda/README.md) | 600,000 | 89 | $499.4 M | $102.3 M | $397.2 M |
| [Kenitra](Kenitra/README.md) | 500,000 | 158 | $782.8 M | $166.3 M | $616.5 M |
| [Tetouan](Tetouan/README.md) | 500,000 | 148 | $862.6 M | $175.6 M | $687.0 M |
| [Safi](Safi/README.md) | 350,000 | 111 | $572.3 M | $120.2 M | $452.1 M |
| [Beni Mellal](Beni-Mellal/README.md) | 300,000 | 55 | $380.0 M | $71.6 M | $308.4 M |
| [Khouribga](Khouribga/README.md) | 250,000 | 39 | $278.9 M | $53.0 M | $225.9 M |
| [Nador](Nador/README.md) | 250,000 | 62 | $408.4 M | $77.0 M | $331.4 M |

## Local Basis And Regeneration

Country finance parameters use `MA` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
