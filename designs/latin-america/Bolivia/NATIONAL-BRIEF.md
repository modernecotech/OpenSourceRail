# Bolivia National OpenSourceRail Strategy

This page contains only Bolivia-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$3.28 B (86.9%) of external capital** and **$4.03 B of external interest**. Capital plus saved interest totals **$7.31 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 1,815,000 |
| Trainsets / vehicle modules | 285 / 1,140 |
| City infrastructure and fleet CAPEX | $2.02 B |
| Shared national factory | $68.4 M |
| Factory sizing basis | 1,140 modules for La Paz, then reused nationally |
| **Total national programme** | **$2.10 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $494.3 M (23.6%) |
| Domestic / local capital | $1.60 B (76.4%) |
| Annual external capital draw | $98.9 M / yr |
| Annual local capital draw | $320.5 M / yr |
| Annual public construction commitment | $221.0 M / yr for 5 years |
| Annual post-grace debt service | $167.1 M / yr |
| Default foreign-turnkey external capital | $3.77 B |
| External capital saved | $3.28 B |
| Capital + lifetime external interest saved | $7.31 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $813.9 M | $122.1 M | $691.8 M |
| Stations | $471.0 M | $94.2 M | $376.8 M |
| Depots | $8.0 M | $2.0 M | $6.0 M |
| Rolling stock | $319.2 M | $111.7 M | $207.5 M |
| Dedicated solar plants | $260.4 M | $117.2 M | $143.2 M |
| Residual train control | $11.2 M | $5.6 M | $5.6 M |
| Charging microgrids | $24.5 M | $9.8 M | $14.7 M |
| EPC / project services | $120.1 M | $18.0 M | $102.1 M |
| Shared national trainset factory | $68.4 M | $13.7 M | $54.7 M |
| **Total** | **$2.10 B** | **$494.3 M** | **$1.60 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [La Paz](La-Paz/README.md) | 1,815,000 | 285 | $2.02 B | $479.9 M | $1.54 B |

## Local Basis And Regeneration

Country finance parameters use `BO` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 scripts/generate-national-briefs.py
```
