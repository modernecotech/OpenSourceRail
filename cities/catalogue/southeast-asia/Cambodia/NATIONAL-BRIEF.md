# Cambodia National OpenSourceRail Strategy

This page contains only Cambodia-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$7.05 B (89.1%) of external capital** and **$8.84 B of external interest**. Capital plus saved interest totals **$15.90 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 2,281,000 |
| Trainsets / vehicle modules | 265 / 1,060 |
| City infrastructure and fleet CAPEX | $3.53 B |
| Shared national factory | $815.5 M |
| Factory sizing basis | 1,060 modules for Phnom Penh, then reused nationally |
| **Total national programme** | **$4.40 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $866.7 M (19.7%) |
| Domestic / local capital | $3.53 B (80.3%) |
| Annual external capital draw | $123.8 M / yr |
| Annual local capital draw | $504.9 M / yr |
| Annual public construction commitment | $366.2 M / yr for 7 years |
| Annual post-grace debt service | $296.5 M / yr |
| Default foreign-turnkey external capital | $7.92 B |
| External capital saved | $7.05 B |
| Capital + lifetime external interest saved | $15.90 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $2.31 B | $346.8 M | $1.97 B |
| Stations | $321.0 M | $64.2 M | $256.8 M |
| Depots | $120.7 M | $30.2 M | $90.5 M |
| Rolling stock | $296.8 M | $103.9 M | $192.9 M |
| Dedicated solar plants | $234.4 M | $105.5 M | $128.9 M |
| Residual train control | $10.5 M | $5.3 M | $5.3 M |
| Charging microgrids | $17.3 M | $6.9 M | $10.4 M |
| EPC / project services | $272.6 M | $40.9 M | $231.7 M |
| Shared national trainset factory | $815.5 M | $163.1 M | $652.4 M |
| **Total** | **$4.40 B** | **$866.7 M** | **$3.53 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Phnom Penh](Phnom-Penh/README.md) | 2,281,000 | 265 | $3.53 B | $695.1 M | $2.83 B |

## Local Basis And Regeneration

Country finance parameters use `KH` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
