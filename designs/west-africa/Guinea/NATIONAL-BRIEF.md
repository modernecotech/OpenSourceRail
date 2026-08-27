# Guinea National OpenSourceRail Strategy

This page contains only Guinea-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$956.7 M (86.6%) of external capital** and **$1.24 B of external interest**. Capital plus saved interest totals **$2.19 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 2,010,000 |
| Trainsets / vehicle modules | 84 / 336 |
| City infrastructure and fleet CAPEX | $592.3 M |
| Shared national factory | $20.2 M |
| Factory sizing basis | 336 modules for Conakry, then reused nationally |
| **Total national programme** | **$613.8 M** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $148.2 M (24.1%) |
| Domestic / local capital | $465.6 M (75.9%) |
| Annual external capital draw | $14.8 M / yr |
| Annual local capital draw | $46.6 M / yr |
| Annual public construction commitment | $53.2 M / yr for 10 years |
| Annual post-grace debt service | $48.6 M / yr |
| Default foreign-turnkey external capital | $1.10 B |
| External capital saved | $956.7 M |
| Capital + lifetime external interest saved | $2.19 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $243.4 M | $36.5 M | $206.9 M |
| Stations | $113.5 M | $22.7 M | $90.8 M |
| Depots | $8.0 M | $2.0 M | $6.0 M |
| Rolling stock | $94.1 M | $32.9 M | $61.2 M |
| Dedicated solar plants | $87.6 M | $39.4 M | $48.2 M |
| Residual train control | $4.1 M | $2.0 M | $2.0 M |
| Charging microgrids | $8.6 M | $3.4 M | $5.1 M |
| EPC / project services | $34.4 M | $5.2 M | $29.3 M |
| Shared national trainset factory | $20.2 M | $4.0 M | $16.1 M |
| **Total** | **$613.8 M** | **$148.2 M** | **$465.6 M** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Conakry](Conakry/README.md) | 2,010,000 | 84 | $592.3 M | $144.0 M | $448.3 M |

## Local Basis And Regeneration

Country finance parameters use `GN` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 scripts/generate-national-briefs.py
```
