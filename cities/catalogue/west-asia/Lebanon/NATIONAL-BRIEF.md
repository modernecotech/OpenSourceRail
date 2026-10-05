# Lebanon National OpenSourceRail Strategy

This page contains only Lebanon-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$5.36 B (88.7%) of external capital** and **$6.79 B of external interest**. Capital plus saved interest totals **$12.15 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 3 |
| Represented population | 3,230,000 |
| Trainsets / vehicle modules | 357 / 1,191 |
| City infrastructure and fleet CAPEX | $2.75 B |
| Shared national factory | $563.3 M |
| Factory sizing basis | 696 modules for Beirut, then reused nationally |
| **Total national programme** | **$3.36 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $681.4 M (20.3%) |
| Domestic / local capital | $2.68 B (79.7%) |
| Annual external capital draw | $85.2 M / yr |
| Annual local capital draw | $334.5 M / yr |
| Annual public construction commitment | $632.8 M / yr for 8 years |
| Annual post-grace debt service | $576.2 M / yr |
| Default foreign-turnkey external capital | $6.04 B |
| External capital saved | $5.36 B |
| Capital + lifetime external interest saved | $12.15 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $1.57 B | $235.6 M | $1.34 B |
| Stations | $319.3 M | $63.9 M | $255.4 M |
| Depots | $198.2 M | $49.6 M | $148.7 M |
| Rolling stock | $341.2 M | $119.4 M | $221.8 M |
| Dedicated solar plants | $127.1 M | $57.2 M | $69.9 M |
| Residual train control | $9.3 M | $4.6 M | $4.6 M |
| Charging microgrids | $16.9 M | $6.7 M | $10.1 M |
| EPC / project services | $211.3 M | $31.7 M | $179.6 M |
| Shared national trainset factory | $563.3 M | $112.7 M | $450.6 M |
| **Total** | **$3.36 B** | **$681.4 M** | **$2.68 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Beirut](Beirut/README.md) | 2,200,000 | 174 | $1.72 B | $354.5 M | $1.37 B |
| [Tripoli Lb](Tripoli-Lb/README.md) | 730,000 | 129 | $690.5 M | $143.5 M | $547.0 M |
| [Sidon](Sidon/README.md) | 300,000 | 54 | $342.8 M | $64.8 M | $278.0 M |

## Local Basis And Regeneration

Country finance parameters use `LB` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
