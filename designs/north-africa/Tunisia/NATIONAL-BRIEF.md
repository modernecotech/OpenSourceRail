# Tunisia National OpenSourceRail Strategy

This page contains only Tunisia-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$2.89 B (86.9%) of external capital** and **$3.56 B of external interest**. Capital plus saved interest totals **$6.45 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 2,900,000 |
| Trainsets / vehicle modules | 255 / 1,020 |
| City infrastructure and fleet CAPEX | $1.78 B |
| Shared national factory | $61.2 M |
| Factory sizing basis | 1,020 modules for Tunis, then reused nationally |
| **Total national programme** | **$1.85 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $434.8 M (23.5%) |
| Domestic / local capital | $1.41 B (76.5%) |
| Annual external capital draw | $87.0 M / yr |
| Annual local capital draw | $282.8 M / yr |
| Annual public construction commitment | $177.9 M / yr for 5 years |
| Annual post-grace debt service | $132.0 M / yr |
| Default foreign-turnkey external capital | $3.33 B |
| External capital saved | $2.89 B |
| Capital + lifetime external interest saved | $6.45 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $726.7 M | $109.0 M | $617.7 M |
| Stations | $404.9 M | $81.0 M | $323.9 M |
| Depots | $8.0 M | $2.0 M | $6.0 M |
| Rolling stock | $285.6 M | $100.0 M | $185.6 M |
| Dedicated solar plants | $222.3 M | $100.0 M | $122.3 M |
| Residual train control | $11.1 M | $5.5 M | $5.5 M |
| Charging microgrids | $22.7 M | $9.1 M | $13.6 M |
| EPC / project services | $106.4 M | $16.0 M | $90.4 M |
| Shared national trainset factory | $61.2 M | $12.2 M | $49.0 M |
| **Total** | **$1.85 B** | **$434.8 M** | **$1.41 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Tunis](Tunis/README.md) | 2,900,000 | 255 | $1.78 B | $421.9 M | $1.36 B |

## Local Basis And Regeneration

Country finance parameters use `TN` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 scripts/generate-national-briefs.py
```
