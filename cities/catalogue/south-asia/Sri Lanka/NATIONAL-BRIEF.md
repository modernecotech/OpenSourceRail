# Sri Lanka National OpenSourceRail Strategy

This page contains only Sri Lanka-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$12.45 B (87.8%) of external capital** and **$15.61 B of external interest**. Capital plus saved interest totals **$28.06 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 4 |
| Represented population | 7,398,000 |
| Trainsets / vehicle modules | 927 / 4,059 |
| City infrastructure and fleet CAPEX | $7.27 B |
| Shared national factory | $566.2 M |
| Factory sizing basis | 2,556 modules for Colombo, then reused nationally |
| **Total national programme** | **$7.88 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.73 B (21.9%) |
| Domestic / local capital | $6.15 B (78.1%) |
| Annual external capital draw | $246.8 M / yr |
| Annual local capital draw | $878.6 M / yr |
| Annual public construction commitment | $917.7 M / yr for 7 years |
| Annual post-grace debt service | $776.0 M / yr |
| Default foreign-turnkey external capital | $14.18 B |
| External capital saved | $12.45 B |
| Capital + lifetime external interest saved | $28.06 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $3.86 B | $579.5 M | $3.28 B |
| Stations | $713.9 M | $142.8 M | $571.1 M |
| Depots | $393.4 M | $98.4 M | $295.1 M |
| Rolling stock | $1.17 B | $408.3 M | $758.3 M |
| Dedicated solar plants | $634.1 M | $285.3 M | $348.7 M |
| Residual train control | $22.0 M | $11.0 M | $11.0 M |
| Charging microgrids | $44.2 M | $17.7 M | $26.6 M |
| EPC / project services | $473.9 M | $71.1 M | $402.8 M |
| Shared national trainset factory | $566.2 M | $113.2 M | $453.0 M |
| **Total** | **$7.88 B** | **$1.73 B** | **$6.15 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Colombo](Colombo/README.md) | 5,648,000 | 426 | $4.62 B | $1.05 B | $3.58 B |
| [Kandy](Kandy/README.md) | 650,000 | 187 | $1.08 B | $222.7 M | $853.7 M |
| [Jaffna](Jaffna/README.md) | 600,000 | 143 | $725.5 M | $156.0 M | $569.4 M |
| [Galle](Galle/README.md) | 500,000 | 171 | $847.0 M | $182.1 M | $665.0 M |

## Local Basis And Regeneration

Country finance parameters use `LK` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
