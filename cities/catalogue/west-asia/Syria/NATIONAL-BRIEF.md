# Syria National OpenSourceRail Strategy

This page contains only Syria-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$22.99 B (89.7%) of external capital** and **$29.70 B of external interest**. Capital plus saved interest totals **$52.69 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 9 |
| Represented population | 7,617,000 |
| Trainsets / vehicle modules | 1,168 / 3,828 |
| City infrastructure and fleet CAPEX | $13.50 B |
| Shared national factory | $698.7 M |
| Factory sizing basis | 888 modules for Damascus, then reused nationally |
| **Total national programme** | **$14.24 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $2.65 B (18.6%) |
| Domestic / local capital | $11.60 B (81.4%) |
| Annual external capital draw | $264.7 M / yr |
| Annual local capital draw | $1.16 B / yr |
| Annual public construction commitment | $2.21 B / yr for 10 years |
| Annual post-grace debt service | $2.03 B / yr |
| Default foreign-turnkey external capital | $25.64 B |
| External capital saved | $22.99 B |
| Capital + lifetime external interest saved | $52.69 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $9.24 B | $1.39 B | $7.85 B |
| Stations | $1.27 B | $254.6 M | $1.02 B |
| Depots | $572.1 M | $143.0 M | $429.1 M |
| Rolling stock | $1.11 B | $388.3 M | $721.1 M |
| Dedicated solar plants | $367.7 M | $165.5 M | $202.2 M |
| Residual train control | $28.7 M | $14.3 M | $14.3 M |
| Charging microgrids | $49.4 M | $19.7 M | $29.6 M |
| EPC / project services | $907.7 M | $136.2 M | $771.6 M |
| Shared national trainset factory | $698.7 M | $139.7 M | $559.0 M |
| **Total** | **$14.24 B** | **$2.65 B** | **$11.60 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Damascus](Damascus/README.md) | 2,503,000 | 222 | $4.92 B | $865.6 M | $4.06 B |
| [Aleppo](Aleppo/README.md) | 1,639,000 | 211 | $2.52 B | $502.2 M | $2.02 B |
| [Homs](Homs/README.md) | 775,000 | 105 | $622.2 M | $126.9 M | $495.3 M |
| [Latakia](Latakia/README.md) | 700,000 | 92 | $2.34 B | $378.6 M | $1.96 B |
| [Hama](Hama/README.md) | 600,000 | 134 | $766.2 M | $156.7 M | $609.6 M |
| [Deir Ez Zor](Deir-Ez-Zor/README.md) | 500,000 | 160 | $877.9 M | $180.8 M | $697.1 M |
| [Raqqa](Raqqa/README.md) | 350,000 | 135 | $710.6 M | $148.8 M | $561.8 M |
| [Idlib](Idlib/README.md) | 300,000 | 59 | $391.9 M | $74.5 M | $317.4 M |
| [Tartus](Tartus/README.md) | 250,000 | 50 | $348.5 M | $65.7 M | $282.8 M |

## Local Basis And Regeneration

Country finance parameters use `SY` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
