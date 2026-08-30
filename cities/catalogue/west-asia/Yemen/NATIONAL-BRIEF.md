# Yemen National OpenSourceRail Strategy

This page contains only Yemen-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$7.58 B (86.2%) of external capital** and **$9.80 B of external interest**. Capital plus saved interest totals **$17.38 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 9 |
| Represented population | 8,337,500 |
| Trainsets / vehicle modules | 1,054 / 4,060 |
| City infrastructure and fleet CAPEX | $4.75 B |
| Shared national factory | $128.9 M |
| Factory sizing basis | 2,148 modules for Sanaa, then reused nationally |
| **Total national programme** | **$4.89 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.21 B (24.8%) |
| Domestic / local capital | $3.68 B (75.2%) |
| Annual external capital draw | $121.1 M / yr |
| Annual local capital draw | $367.6 M / yr |
| Annual public construction commitment | $657.3 M / yr for 10 years |
| Annual post-grace debt service | $607.3 M / yr |
| Default foreign-turnkey external capital | $8.80 B |
| External capital saved | $7.58 B |
| Capital + lifetime external interest saved | $17.38 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $1.62 B | $243.1 M | $1.38 B |
| Stations | $1.01 B | $201.7 M | $806.7 M |
| Depots | $72.0 M | $18.0 M | $54.0 M |
| Rolling stock | $1.17 B | $408.8 M | $759.2 M |
| Dedicated solar plants | $535.6 M | $241.0 M | $294.6 M |
| Residual train control | $27.3 M | $13.7 M | $13.7 M |
| Charging microgrids | $40.9 M | $16.4 M | $24.5 M |
| EPC / project services | $284.6 M | $42.7 M | $241.9 M |
| Shared national trainset factory | $128.9 M | $25.8 M | $103.1 M |
| **Total** | **$4.89 B** | **$1.21 B** | **$3.68 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Sanaa](Sanaa/README.md) | 3,937,500 | 358 | $2.15 B | $574.5 M | $1.58 B |
| [Aden](Aden/README.md) | 985,000 | 97 | $376.8 M | $90.4 M | $286.4 M |
| [Hodeidah](Hodeidah/README.md) | 750,000 | 71 | $291.3 M | $68.5 M | $222.8 M |
| [Ibb](Ibb/README.md) | 750,000 | 106 | $409.3 M | $98.1 M | $311.2 M |
| [Taiz](Taiz/README.md) | 615,000 | 94 | $359.0 M | $86.0 M | $273.1 M |
| [Mukalla](Mukalla/README.md) | 550,000 | 152 | $462.3 M | $117.1 M | $345.2 M |
| [Dhamar](Dhamar/README.md) | 300,000 | 63 | $204.6 M | $45.3 M | $159.3 M |
| [Lahij](Lahij/README.md) | 250,000 | 59 | $288.8 M | $59.8 M | $229.0 M |
| [Sayun](Sayun/README.md) | 200,000 | 54 | $206.6 M | $44.3 M | $162.3 M |

## Local Basis And Regeneration

Country finance parameters use `YE` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
