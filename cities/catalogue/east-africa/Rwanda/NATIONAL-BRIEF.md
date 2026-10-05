# Rwanda National OpenSourceRail Strategy

This page contains only Rwanda-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$6.24 B (88.9%) of external capital** and **$7.82 B of external interest**. Capital plus saved interest totals **$14.05 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 3 |
| Represented population | 1,708,000 |
| Trainsets / vehicle modules | 347 / 1,076 |
| City infrastructure and fleet CAPEX | $3.24 B |
| Shared national factory | $609.6 M |
| Factory sizing basis | 764 modules for Kigali, then reused nationally |
| **Total national programme** | **$3.90 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $777.1 M (19.9%) |
| Domestic / local capital | $3.12 B (80.1%) |
| Annual external capital draw | $111.0 M / yr |
| Annual local capital draw | $445.5 M / yr |
| Annual public construction commitment | $336.1 M / yr for 7 years |
| Annual post-grace debt service | $273.1 M / yr |
| Default foreign-turnkey external capital | $7.01 B |
| External capital saved | $6.24 B |
| Capital + lifetime external interest saved | $14.05 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $1.95 B | $292.5 M | $1.66 B |
| Stations | $384.6 M | $76.9 M | $307.7 M |
| Depots | $195.1 M | $48.8 M | $146.3 M |
| Rolling stock | $301.3 M | $105.4 M | $195.8 M |
| Dedicated solar plants | $181.7 M | $81.8 M | $100.0 M |
| Residual train control | $11.6 M | $5.8 M | $5.8 M |
| Charging microgrids | $18.9 M | $7.6 M | $11.4 M |
| EPC / project services | $243.0 M | $36.4 M | $206.5 M |
| Shared national trainset factory | $609.6 M | $121.9 M | $487.7 M |
| **Total** | **$3.90 B** | **$777.1 M** | **$3.12 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Kigali](Kigali/README.md) | 1,208,000 | 191 | $2.28 B | $462.8 M | $1.82 B |
| [Huye](Huye/README.md) | 250,000 | 80 | $480.3 M | $93.0 M | $387.3 M |
| [Rubavu](Rubavu/README.md) | 250,000 | 76 | $482.9 M | $93.1 M | $389.8 M |

## Local Basis And Regeneration

Country finance parameters use `RW` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
