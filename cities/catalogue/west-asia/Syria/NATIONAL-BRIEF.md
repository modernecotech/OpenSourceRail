# Syria National OpenSourceRail Strategy

This page contains only Syria-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$15.99 B (88.8%) of external capital** and **$20.66 B of external interest**. Capital plus saved interest totals **$36.65 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 9 |
| Represented population | 7,617,000 |
| Trainsets / vehicle modules | 1,168 / 3,828 |
| City infrastructure and fleet CAPEX | $9.25 B |
| Shared national factory | $698.7 M |
| Factory sizing basis | 888 modules for Damascus, then reused nationally |
| **Total national programme** | **$10.00 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $2.01 B (20.1%) |
| Domestic / local capital | $7.99 B (79.9%) |
| Annual external capital draw | $201.1 M / yr |
| Annual local capital draw | $799.1 M / yr |
| Annual public construction commitment | $1.53 B / yr for 10 years |
| Annual post-grace debt service | $1.41 B / yr |
| Default foreign-turnkey external capital | $18.00 B |
| External capital saved | $15.99 B |
| Capital + lifetime external interest saved | $36.65 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $5.27 B | $790.9 M | $4.48 B |
| Stations | $1.27 B | $254.6 M | $1.02 B |
| Depots | $572.1 M | $143.0 M | $429.1 M |
| Rolling stock | $1.11 B | $388.3 M | $721.1 M |
| Dedicated solar plants | $367.7 M | $165.5 M | $202.2 M |
| Residual train control | $28.7 M | $14.3 M | $14.3 M |
| Charging microgrids | $49.4 M | $19.7 M | $29.6 M |
| EPC / project services | $630.3 M | $94.5 M | $535.7 M |
| Shared national trainset factory | $698.7 M | $139.7 M | $559.0 M |
| **Total** | **$10.00 B** | **$2.01 B** | **$7.99 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Damascus](Damascus/README.md) | 2,503,000 | 222 | $2.57 B | $512.2 M | $2.06 B |
| [Aleppo](Aleppo/README.md) | 1,639,000 | 211 | $2.48 B | $496.7 M | $1.98 B |
| [Homs](Homs/README.md) | 775,000 | 105 | $622.2 M | $126.9 M | $495.3 M |
| [Latakia](Latakia/README.md) | 700,000 | 92 | $486.5 M | $101.3 M | $385.2 M |
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
