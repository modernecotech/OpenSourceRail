# Myanmar National OpenSourceRail Strategy

This page contains only Myanmar-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$10.19 B (85.8%) of external capital** and **$13.16 B of external interest**. Capital plus saved interest totals **$23.34 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 2 |
| Represented population | 6,926,000 |
| Trainsets / vehicle modules | 937 / 5,070 |
| City infrastructure and fleet CAPEX | $6.34 B |
| Shared national factory | $238.0 M |
| Factory sizing basis | 3,966 modules for Yangon, then reused nationally |
| **Total national programme** | **$6.59 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.68 B (25.5%) |
| Domestic / local capital | $4.91 B (74.5%) |
| Annual external capital draw | $168.2 M / yr |
| Annual local capital draw | $491.1 M / yr |
| Annual public construction commitment | $684.7 M / yr for 10 years |
| Annual post-grace debt service | $627.4 M / yr |
| Default foreign-turnkey external capital | $11.87 B |
| External capital saved | $10.19 B |
| Capital + lifetime external interest saved | $23.34 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $2.27 B | $341.2 M | $1.93 B |
| Stations | $1.15 B | $229.3 M | $917.2 M |
| Depots | $16.0 M | $4.0 M | $12.0 M |
| Rolling stock | $1.42 B | $496.9 M | $922.7 M |
| Dedicated solar plants | $1.03 B | $462.8 M | $565.6 M |
| Residual train control | $32.0 M | $16.0 M | $16.0 M |
| Charging microgrids | $74.5 M | $29.8 M | $44.7 M |
| EPC / project services | $364.1 M | $54.6 M | $309.5 M |
| Shared national trainset factory | $238.0 M | $47.6 M | $190.4 M |
| **Total** | **$6.59 B** | **$1.68 B** | **$4.91 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Yangon](Yangon/README.md) | 5,200,000 | 661 | $4.40 B | $1.19 B | $3.21 B |
| [Mandalay](Mandalay/README.md) | 1,726,000 | 276 | $1.94 B | $443.5 M | $1.50 B |

## Local Basis And Regeneration

Country finance parameters use `MM` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 scripts/generate-national-briefs.py
```
