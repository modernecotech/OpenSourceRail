# South Africa National OpenSourceRail Strategy

This page contains only South Africa-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$10.16 B (85.8%) of external capital** and **$12.49 B of external interest**. Capital plus saved interest totals **$22.66 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 5 |
| Represented population | 6,200,000 |
| Trainsets / vehicle modules | 1,096 / 5,056 |
| City infrastructure and fleet CAPEX | $6.34 B |
| Shared national factory | $221.8 M |
| Factory sizing basis | 3,696 modules for Durban, then reused nationally |
| **Total national programme** | **$6.58 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.68 B (25.6%) |
| Domestic / local capital | $4.90 B (74.4%) |
| Annual external capital draw | $336.4 M / yr |
| Annual local capital draw | $979.6 M / yr |
| Annual public construction commitment | $683.0 M / yr for 5 years |
| Annual post-grace debt service | $520.6 M / yr |
| Default foreign-turnkey external capital | $11.84 B |
| External capital saved | $10.16 B |
| Capital + lifetime external interest saved | $22.66 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $2.12 B | $317.9 M | $1.80 B |
| Stations | $1.30 B | $259.7 M | $1.04 B |
| Depots | $40.0 M | $10.0 M | $30.0 M |
| Rolling stock | $1.44 B | $503.9 M | $935.8 M |
| Dedicated solar plants | $999.1 M | $449.6 M | $549.5 M |
| Residual train control | $31.5 M | $15.8 M | $15.8 M |
| Charging microgrids | $64.8 M | $25.9 M | $38.9 M |
| EPC / project services | $365.1 M | $54.8 M | $310.3 M |
| Shared national trainset factory | $221.8 M | $44.4 M | $177.4 M |
| **Total** | **$6.58 B** | **$1.68 B** | **$4.90 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Durban](Durban/README.md) | 3,900,000 | 616 | $4.51 B | $1.19 B | $3.33 B |
| [East London Za](East-London-Za/README.md) | 800,000 | 139 | $538.7 M | $136.2 M | $402.5 M |
| [Bloemfontein](Bloemfontein/README.md) | 600,000 | 151 | $616.2 M | $154.3 M | $462.0 M |
| [Polokwane](Polokwane/README.md) | 600,000 | 110 | $383.6 M | $93.9 M | $289.6 M |
| [Nelspruit](Nelspruit/README.md) | 300,000 | 80 | $292.5 M | $65.2 M | $227.3 M |

## Local Basis And Regeneration

Country finance parameters use `ZA` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 scripts/generate-national-briefs.py
```
