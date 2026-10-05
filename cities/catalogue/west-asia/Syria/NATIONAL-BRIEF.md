# Syria National OpenSourceRail Strategy

This page contains only Syria-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$15.25 B (88.9%) of external capital** and **$19.70 B of external interest**. Capital plus saved interest totals **$34.96 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 9 |
| Represented population | 7,617,000 |
| Trainsets / vehicle modules | 1,127 / 3,683 |
| City infrastructure and fleet CAPEX | $8.83 B |
| Shared national factory | $662.9 M |
| Factory sizing basis | 836 modules for Damascus, then reused nationally |
| **Total national programme** | **$9.54 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.91 B (20.1%) |
| Domestic / local capital | $7.62 B (79.9%) |
| Annual external capital draw | $191.3 M / yr |
| Annual local capital draw | $762.4 M / yr |
| Annual public construction commitment | $1.46 B / yr for 10 years |
| Annual post-grace debt service | $1.34 B / yr |
| Default foreign-turnkey external capital | $17.17 B |
| External capital saved | $15.25 B |
| Capital + lifetime external interest saved | $34.96 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $5.27 B | $789.8 M | $4.48 B |
| Stations | $932.6 M | $186.5 M | $746.1 M |
| Depots | $564.7 M | $141.2 M | $423.5 M |
| Rolling stock | $1.07 B | $373.7 M | $694.0 M |
| Dedicated solar plants | $372.2 M | $167.5 M | $204.7 M |
| Residual train control | $28.6 M | $14.3 M | $14.3 M |
| Charging microgrids | $43.0 M | $17.2 M | $25.8 M |
| EPC / project services | $599.5 M | $89.9 M | $509.6 M |
| Shared national trainset factory | $662.9 M | $132.6 M | $530.3 M |
| **Total** | **$9.54 B** | **$1.91 B** | **$7.62 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Damascus](Damascus/README.md) | 2,503,000 | 209 | $2.43 B | $483.1 M | $1.95 B |
| [Aleppo](Aleppo/README.md) | 1,639,000 | 202 | $2.36 B | $471.6 M | $1.89 B |
| [Homs](Homs/README.md) | 775,000 | 105 | $610.4 M | $124.6 M | $485.9 M |
| [Latakia](Latakia/README.md) | 700,000 | 90 | $477.6 M | $99.5 M | $378.2 M |
| [Hama](Hama/README.md) | 600,000 | 129 | $730.2 M | $148.9 M | $581.3 M |
| [Deir Ez Zor](Deir-Ez-Zor/README.md) | 500,000 | 155 | $838.2 M | $172.6 M | $665.5 M |
| [Raqqa](Raqqa/README.md) | 350,000 | 128 | $672.6 M | $140.4 M | $532.2 M |
| [Idlib](Idlib/README.md) | 300,000 | 61 | $370.5 M | $70.5 M | $300.0 M |
| [Tartus](Tartus/README.md) | 250,000 | 48 | $329.9 M | $61.8 M | $268.0 M |

## Local Basis And Regeneration

Country finance parameters use `SY` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
