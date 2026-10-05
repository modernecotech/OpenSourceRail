# Palestine National OpenSourceRail Strategy

This page contains only Palestine-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$4.31 B (88.3%) of external capital** and **$5.41 B of external interest**. Capital plus saved interest totals **$9.72 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 3 |
| Represented population | 1,850,000 |
| Trainsets / vehicle modules | 432 / 1,296 |
| City infrastructure and fleet CAPEX | $2.11 B |
| Shared national factory | $559.9 M |
| Factory sizing basis | 564 modules for Nablus, then reused nationally |
| **Total national programme** | **$2.71 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $569.1 M (21.0%) |
| Domestic / local capital | $2.14 B (79.0%) |
| Annual external capital draw | $81.3 M / yr |
| Annual local capital draw | $306.2 M / yr |
| Annual public construction commitment | $232.6 M / yr for 7 years |
| Annual post-grace debt service | $189.8 M / yr |
| Default foreign-turnkey external capital | $4.88 B |
| External capital saved | $4.31 B |
| Capital + lifetime external interest saved | $9.72 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $1.14 B | $170.9 M | $968.5 M |
| Stations | $184.6 M | $36.9 M | $147.7 M |
| Depots | $167.1 M | $41.8 M | $125.3 M |
| Rolling stock | $388.8 M | $136.1 M | $252.7 M |
| Dedicated solar plants | $89.8 M | $40.4 M | $49.4 M |
| Residual train control | $6.9 M | $3.5 M | $3.5 M |
| Charging microgrids | $4.5 M | $1.8 M | $2.7 M |
| EPC / project services | $171.6 M | $25.7 M | $145.9 M |
| Shared national trainset factory | $559.9 M | $112.0 M | $447.9 M |
| **Total** | **$2.71 B** | **$569.1 M** | **$2.14 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Hebron](Hebron/README.md) | 800,000 | 154 | $796.2 M | $167.7 M | $628.5 M |
| [Gaza City](Gaza-City/README.md) | 600,000 | 90 | $438.7 M | $93.3 M | $345.3 M |
| [Nablus](Nablus/README.md) | 450,000 | 188 | $878.8 M | $190.3 M | $688.5 M |

## Local Basis And Regeneration

Country finance parameters use `PS` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
