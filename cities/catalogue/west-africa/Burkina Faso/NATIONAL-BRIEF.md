# Burkina Faso National OpenSourceRail Strategy

This page contains only Burkina Faso-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$5.70 B (89.0%) of external capital** and **$7.36 B of external interest**. Capital plus saved interest totals **$13.06 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 2,531,000 |
| Trainsets / vehicle modules | 248 / 992 |
| City infrastructure and fleet CAPEX | $2.73 B |
| Shared national factory | $771.6 M |
| Factory sizing basis | 992 modules for Ouagadougou, then reused nationally |
| **Total national programme** | **$3.56 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $705.6 M (19.8%) |
| Domestic / local capital | $2.85 B (80.2%) |
| Annual external capital draw | $70.6 M / yr |
| Annual local capital draw | $285.1 M / yr |
| Annual public construction commitment | $305.5 M / yr for 10 years |
| Annual post-grace debt service | $275.3 M / yr |
| Default foreign-turnkey external capital | $6.40 B |
| External capital saved | $5.70 B |
| Capital + lifetime external interest saved | $13.06 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $1.69 B | $254.2 M | $1.44 B |
| Stations | $300.5 M | $60.1 M | $240.4 M |
| Depots | $117.6 M | $29.4 M | $88.2 M |
| Rolling stock | $277.8 M | $97.2 M | $180.5 M |
| Dedicated solar plants | $143.2 M | $64.4 M | $78.8 M |
| Residual train control | $9.7 M | $4.9 M | $4.9 M |
| Charging microgrids | $19.1 M | $7.6 M | $11.4 M |
| EPC / project services | $223.3 M | $33.5 M | $189.8 M |
| Shared national trainset factory | $771.6 M | $154.3 M | $617.3 M |
| **Total** | **$3.56 B** | **$705.6 M** | **$2.85 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Ouagadougou](Ouagadougou/README.md) | 2,531,000 | 248 | $2.73 B | $543.2 M | $2.19 B |

## Local Basis And Regeneration

Country finance parameters use `BF` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
