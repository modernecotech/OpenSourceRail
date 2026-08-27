# Zambia National OpenSourceRail Strategy

This page contains only Zambia-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$4.61 B (85.2%) of external capital** and **$5.78 B of external interest**. Capital plus saved interest totals **$10.39 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 3,037,000 |
| Trainsets / vehicle modules | 418 / 2,508 |
| City infrastructure and fleet CAPEX | $2.84 B |
| Shared national factory | $150.5 M |
| Factory sizing basis | 2,508 modules for Lusaka, then reused nationally |
| **Total national programme** | **$3.00 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $798.2 M (26.6%) |
| Domestic / local capital | $2.21 B (73.4%) |
| Annual external capital draw | $114.0 M / yr |
| Annual local capital draw | $315.1 M / yr |
| Annual public construction commitment | $390.1 M / yr for 7 years |
| Annual post-grace debt service | $339.9 M / yr |
| Default foreign-turnkey external capital | $5.41 B |
| External capital saved | $4.61 B |
| Capital + lifetime external interest saved | $10.39 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $899.3 M | $134.9 M | $764.4 M |
| Stations | $498.3 M | $99.7 M | $398.6 M |
| Depots | $8.0 M | $2.0 M | $6.0 M |
| Rolling stock | $702.2 M | $245.8 M | $456.5 M |
| Dedicated solar plants | $532.0 M | $239.4 M | $292.6 M |
| Residual train control | $14.0 M | $7.0 M | $7.0 M |
| Charging microgrids | $37.9 M | $15.2 M | $22.7 M |
| EPC / project services | $161.7 M | $24.3 M | $137.5 M |
| Shared national trainset factory | $150.5 M | $30.1 M | $120.4 M |
| **Total** | **$3.00 B** | **$798.2 M** | **$2.21 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Lusaka](Lusaka/README.md) | 3,037,000 | 418 | $2.84 B | $766.6 M | $2.08 B |

## Local Basis And Regeneration

Country finance parameters use `ZM` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 scripts/generate-national-briefs.py
```
