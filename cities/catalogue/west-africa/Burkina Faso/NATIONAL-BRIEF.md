# Burkina Faso National OpenSourceRail Strategy

This page contains only Burkina Faso-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$2.81 B (87.0%) of external capital** and **$3.63 B of external interest**. Capital plus saved interest totals **$6.44 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 2,531,000 |
| Trainsets / vehicle modules | 271 / 1,084 |
| City infrastructure and fleet CAPEX | $1.73 B |
| Shared national factory | $65.0 M |
| Factory sizing basis | 1,084 modules for Ouagadougou, then reused nationally |
| **Total national programme** | **$1.80 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $420.9 M (23.4%) |
| Domestic / local capital | $1.37 B (76.6%) |
| Annual external capital draw | $42.1 M / yr |
| Annual local capital draw | $137.5 M / yr |
| Annual public construction commitment | $150.9 M / yr for 10 years |
| Annual post-grace debt service | $137.7 M / yr |
| Default foreign-turnkey external capital | $3.23 B |
| External capital saved | $2.81 B |
| Capital + lifetime external interest saved | $6.44 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $691.2 M | $103.7 M | $587.5 M |
| Stations | $397.8 M | $79.6 M | $318.2 M |
| Depots | $8.0 M | $2.0 M | $6.0 M |
| Rolling stock | $303.5 M | $106.2 M | $197.3 M |
| Dedicated solar plants | $190.0 M | $85.5 M | $104.5 M |
| Residual train control | $11.1 M | $5.5 M | $5.5 M |
| Charging microgrids | $24.1 M | $9.6 M | $14.4 M |
| EPC / project services | $105.0 M | $15.8 M | $89.3 M |
| Shared national trainset factory | $65.0 M | $13.0 M | $52.0 M |
| **Total** | **$1.80 B** | **$420.9 M** | **$1.37 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Ouagadougou](Ouagadougou/README.md) | 2,531,000 | 271 | $1.73 B | $407.2 M | $1.32 B |

## Local Basis And Regeneration

Country finance parameters use `BF` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
