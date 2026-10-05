# Myanmar National OpenSourceRail Strategy

This page contains only Myanmar-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$68.78 B (90.5%) of external capital** and **$88.84 B of external interest**. Capital plus saved interest totals **$157.62 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 2 |
| Represented population | 6,926,000 |
| Trainsets / vehicle modules | 1,089 / 5,968 |
| City infrastructure and fleet CAPEX | $41.27 B |
| Shared national factory | $871.2 M |
| Factory sizing basis | 4,836 modules for Yangon, then reused nationally |
| **Total national programme** | **$42.20 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $7.19 B (17.0%) |
| Domestic / local capital | $35.02 B (83.0%) |
| Annual external capital draw | $718.6 M / yr |
| Annual local capital draw | $3.50 B / yr |
| Annual public construction commitment | $4.67 B / yr for 10 years |
| Annual post-grace debt service | $4.18 B / yr |
| Default foreign-turnkey external capital | $75.96 B |
| External capital saved | $68.78 B |
| Capital + lifetime external interest saved | $157.62 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $33.48 B | $5.02 B | $28.46 B |
| Stations | $1.91 B | $381.4 M | $1.53 B |
| Depots | $437.9 M | $109.5 M | $328.4 M |
| Rolling stock | $1.67 B | $584.9 M | $1.09 B |
| Dedicated solar plants | $1.00 B | $450.7 M | $550.8 M |
| Residual train control | $34.0 M | $17.0 M | $17.0 M |
| Charging microgrids | $105.1 M | $42.0 M | $63.1 M |
| EPC / project services | $2.70 B | $404.3 M | $2.29 B |
| Shared national trainset factory | $871.2 M | $174.2 M | $696.9 M |
| **Total** | **$42.20 B** | **$7.19 B** | **$35.02 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Yangon](Yangon/README.md) | 5,200,000 | 806 | $26.99 B | $4.71 B | $22.29 B |
| [Mandalay](Mandalay/README.md) | 1,726,000 | 283 | $14.27 B | $2.30 B | $11.98 B |

## Local Basis And Regeneration

Country finance parameters use `MM` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
