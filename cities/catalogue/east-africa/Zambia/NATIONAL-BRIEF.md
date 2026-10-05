# Zambia National OpenSourceRail Strategy

This page contains only Zambia-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$7.55 B (87.8%) of external capital** and **$9.46 B of external interest**. Capital plus saved interest totals **$17.01 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 3,037,000 |
| Trainsets / vehicle modules | 357 / 2,142 |
| City infrastructure and fleet CAPEX | $3.92 B |
| Shared national factory | $802.3 M |
| Factory sizing basis | 2,142 modules for Lusaka, then reused nationally |
| **Total national programme** | **$4.78 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.05 B (22.0%) |
| Domestic / local capital | $3.73 B (78.0%) |
| Annual external capital draw | $150.1 M / yr |
| Annual local capital draw | $532.5 M / yr |
| Annual public construction commitment | $645.8 M / yr for 7 years |
| Annual post-grace debt service | $556.9 M / yr |
| Default foreign-turnkey external capital | $8.60 B |
| External capital saved | $7.55 B |
| Capital + lifetime external interest saved | $17.01 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $2.09 B | $312.8 M | $1.77 B |
| Stations | $357.7 M | $71.5 M | $286.2 M |
| Depots | $187.4 M | $46.9 M | $140.6 M |
| Rolling stock | $599.8 M | $209.9 M | $389.8 M |
| Dedicated solar plants | $418.3 M | $188.2 M | $230.1 M |
| Residual train control | $11.9 M | $6.0 M | $6.0 M |
| Charging microgrids | $30.2 M | $12.1 M | $18.1 M |
| EPC / project services | $285.2 M | $42.8 M | $242.4 M |
| Shared national trainset factory | $802.3 M | $160.5 M | $641.8 M |
| **Total** | **$4.78 B** | **$1.05 B** | **$3.73 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Lusaka](Lusaka/README.md) | 3,037,000 | 357 | $3.92 B | $881.7 M | $3.04 B |

## Local Basis And Regeneration

Country finance parameters use `ZM` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
