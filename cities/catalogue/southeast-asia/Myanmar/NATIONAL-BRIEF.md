# Myanmar National OpenSourceRail Strategy

This page contains only Myanmar-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$15.36 B (88.0%) of external capital** and **$19.84 B of external interest**. Capital plus saved interest totals **$35.20 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 2 |
| Represented population | 6,926,000 |
| Trainsets / vehicle modules | 833 / 4,492 |
| City infrastructure and fleet CAPEX | $8.86 B |
| Shared national factory | $786.6 M |
| Factory sizing basis | 3,480 modules for Yangon, then reused nationally |
| **Total national programme** | **$9.70 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $2.10 B (21.6%) |
| Domestic / local capital | $7.60 B (78.4%) |
| Annual external capital draw | $209.6 M / yr |
| Annual local capital draw | $760.2 M / yr |
| Annual public construction commitment | $1.04 B / yr for 10 years |
| Annual post-grace debt service | $940.1 M / yr |
| Default foreign-turnkey external capital | $17.46 B |
| External capital saved | $15.36 B |
| Capital + lifetime external interest saved | $35.20 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $5.05 B | $757.2 M | $4.29 B |
| Stations | $726.4 M | $145.3 M | $581.1 M |
| Depots | $372.7 M | $93.2 M | $279.5 M |
| Rolling stock | $1.26 B | $440.2 M | $817.5 M |
| Dedicated solar plants | $843.6 M | $379.6 M | $464.0 M |
| Residual train control | $28.1 M | $14.1 M | $14.1 M |
| Charging microgrids | $56.2 M | $22.5 M | $33.7 M |
| EPC / project services | $579.3 M | $86.9 M | $492.4 M |
| Shared national trainset factory | $786.6 M | $157.3 M | $629.2 M |
| **Total** | **$9.70 B** | **$2.10 B** | **$7.60 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Yangon](Yangon/README.md) | 5,200,000 | 580 | $6.11 B | $1.38 B | $4.72 B |
| [Mandalay](Mandalay/README.md) | 1,726,000 | 253 | $2.75 B | $547.4 M | $2.20 B |

## Local Basis And Regeneration

Country finance parameters use `MM` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
