# Burkina Faso National OpenSourceRail Strategy

This page contains only Burkina Faso-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$6.02 B (89.0%) of external capital** and **$7.77 B of external interest**. Capital plus saved interest totals **$13.79 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 2,531,000 |
| Trainsets / vehicle modules | 262 / 1,048 |
| City infrastructure and fleet CAPEX | $2.89 B |
| Shared national factory | $809.0 M |
| Factory sizing basis | 1,048 modules for Ouagadougou, then reused nationally |
| **Total national programme** | **$3.76 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $746.4 M (19.9%) |
| Domestic / local capital | $3.01 B (80.1%) |
| Annual external capital draw | $74.6 M / yr |
| Annual local capital draw | $301.0 M / yr |
| Annual public construction commitment | $322.6 M / yr for 10 years |
| Annual post-grace debt service | $290.7 M / yr |
| Default foreign-turnkey external capital | $6.76 B |
| External capital saved | $6.02 B |
| Capital + lifetime external interest saved | $13.79 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $1.71 B | $256.9 M | $1.46 B |
| Stations | $413.0 M | $82.6 M | $330.4 M |
| Depots | $119.5 M | $29.9 M | $89.6 M |
| Rolling stock | $293.4 M | $102.7 M | $190.7 M |
| Dedicated solar plants | $140.8 M | $63.4 M | $77.5 M |
| Residual train control | $9.7 M | $4.9 M | $4.9 M |
| Charging microgrids | $22.1 M | $8.8 M | $13.2 M |
| EPC / project services | $236.6 M | $35.5 M | $201.1 M |
| Shared national trainset factory | $809.0 M | $161.8 M | $647.2 M |
| **Total** | **$3.76 B** | **$746.4 M** | **$3.01 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Ouagadougou](Ouagadougou/README.md) | 2,531,000 | 262 | $2.89 B | $576.1 M | $2.32 B |

## Local Basis And Regeneration

Country finance parameters use `BF` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
