# Rwanda National OpenSourceRail Strategy

This page contains only Rwanda-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$3.77 B (87.1%) of external capital** and **$4.73 B of external interest**. Capital plus saved interest totals **$8.50 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 3 |
| Represented population | 1,708,000 |
| Trainsets / vehicle modules | 410 / 1,274 |
| City infrastructure and fleet CAPEX | $2.35 B |
| Shared national factory | $54.5 M |
| Factory sizing basis | 908 modules for Kigali, then reused nationally |
| **Total national programme** | **$2.41 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $560.5 M (23.3%) |
| Domestic / local capital | $1.85 B (76.7%) |
| Annual external capital draw | $80.1 M / yr |
| Annual local capital draw | $263.7 M / yr |
| Annual public construction commitment | $203.5 M / yr for 7 years |
| Annual post-grace debt service | $167.6 M / yr |
| Default foreign-turnkey external capital | $4.33 B |
| External capital saved | $3.77 B |
| Capital + lifetime external interest saved | $8.50 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $884.6 M | $132.7 M | $751.9 M |
| Stations | $641.6 M | $128.3 M | $513.3 M |
| Depots | $24.0 M | $6.0 M | $18.0 M |
| Rolling stock | $356.7 M | $124.9 M | $231.9 M |
| Dedicated solar plants | $265.7 M | $119.6 M | $146.1 M |
| Residual train control | $13.7 M | $6.9 M | $6.9 M |
| Charging microgrids | $25.9 M | $10.3 M | $15.5 M |
| EPC / project services | $140.1 M | $21.0 M | $119.1 M |
| Shared national trainset factory | $54.5 M | $10.9 M | $43.6 M |
| **Total** | **$2.41 B** | **$560.5 M** | **$1.85 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Kigali](Kigali/README.md) | 1,208,000 | 227 | $1.74 B | $409.8 M | $1.33 B |
| [Huye](Huye/README.md) | 250,000 | 92 | $294.3 M | $67.7 M | $226.6 M |
| [Rubavu](Rubavu/README.md) | 250,000 | 91 | $315.3 M | $71.6 M | $243.7 M |

## Local Basis And Regeneration

Country finance parameters use `RW` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
