# South Sudan National OpenSourceRail Strategy

**Uncalibrated country scenario.** Uncalibrated generic XX scenario; obtain South Sudan income, lending, FX and market-access evidence before appraisal. Numerical XX defaults are illustrative, not South Sudan country estimates or available financing.

This page contains only South Sudan-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$740.7 M (89.2%) of external capital** and **$910.6 M of external interest**. Capital plus saved interest totals **$1.65 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 300,000 |
| Trainsets / vehicle modules | 40 / 80 |
| City infrastructure and fleet CAPEX | $266.9 M |
| Shared national factory | $181.7 M |
| Factory sizing basis | 80 modules for Wau, then reused nationally |
| **Total national programme** | **$461.3 M** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $89.7 M (19.4%) |
| Domestic / local capital | $371.6 M (80.6%) |
| Annual external capital draw | $17.9 M / yr |
| Annual local capital draw | $74.3 M / yr |
| Annual public construction commitment | $39.7 M / yr for 5 years |
| Annual post-grace debt service | $28.1 M / yr |
| Default foreign-turnkey external capital | $830.4 M |
| External capital saved | $740.7 M |
| Capital + lifetime external interest saved | $1.65 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $137.1 M | $20.6 M | $116.5 M |
| Stations | $48.5 M | $9.7 M | $38.8 M |
| Depots | $39.6 M | $9.9 M | $29.7 M |
| Rolling stock | $22.4 M | $7.8 M | $14.6 M |
| Residual train control | $763 k | $382 k | $382 k |
| Charging microgrids | $1.1 M | $460 k | $690 k |
| EPC / project services | $30.2 M | $4.5 M | $25.7 M |
| Shared national trainset factory | $181.7 M | $36.3 M | $145.4 M |
| **Total** | **$461.3 M** | **$89.7 M** | **$371.6 M** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Wau](Wau/README.md) | 300,000 | 40 | $266.9 M | $51.4 M | $215.4 M |

## Local Basis And Regeneration

Country finance parameters use `SS` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
