# Mali National OpenSourceRail Strategy

This page contains only Mali-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$6.34 B (89.4%) of external capital** and **$8.19 B of external interest**. Capital plus saved interest totals **$14.54 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 2,929,000 |
| Trainsets / vehicle modules | 233 / 932 |
| City infrastructure and fleet CAPEX | $3.16 B |
| Shared national factory | $733.0 M |
| Factory sizing basis | 932 modules for Bamako, then reused nationally |
| **Total national programme** | **$3.94 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $755.4 M (19.2%) |
| Domestic / local capital | $3.19 B (80.8%) |
| Annual external capital draw | $75.5 M / yr |
| Annual local capital draw | $318.9 M / yr |
| Annual public construction commitment | $340.1 M / yr for 10 years |
| Annual post-grace debt service | $305.8 M / yr |
| Default foreign-turnkey external capital | $7.10 B |
| External capital saved | $6.34 B |
| Capital + lifetime external interest saved | $14.54 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $2.15 B | $322.8 M | $1.83 B |
| Stations | $265.0 M | $53.0 M | $212.0 M |
| Depots | $115.8 M | $28.9 M | $86.8 M |
| Rolling stock | $261.0 M | $91.3 M | $169.6 M |
| Dedicated solar plants | $140.7 M | $63.3 M | $77.4 M |
| Residual train control | $9.7 M | $4.8 M | $4.8 M |
| Charging microgrids | $18.1 M | $7.3 M | $10.9 M |
| EPC / project services | $248.8 M | $37.3 M | $211.5 M |
| Shared national trainset factory | $733.0 M | $146.6 M | $586.4 M |
| **Total** | **$3.94 B** | **$755.4 M** | **$3.19 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Bamako](Bamako/README.md) | 2,929,000 | 233 | $3.16 B | $601.1 M | $2.56 B |

## Local Basis And Regeneration

Country finance parameters use `ML` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
