# Mali National OpenSourceRail Strategy

This page contains only Mali-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$3.48 B (88.1%) of external capital** and **$4.50 B of external interest**. Capital plus saved interest totals **$7.98 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 2,929,000 |
| Trainsets / vehicle modules | 255 / 1,020 |
| City infrastructure and fleet CAPEX | $2.13 B |
| Shared national factory | $61.2 M |
| Factory sizing basis | 1,020 modules for Bamako, then reused nationally |
| **Total national programme** | **$2.20 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $470.7 M (21.4%) |
| Domestic / local capital | $1.73 B (78.6%) |
| Annual external capital draw | $47.1 M / yr |
| Annual local capital draw | $172.5 M / yr |
| Annual public construction commitment | $186.8 M / yr for 10 years |
| Annual post-grace debt service | $169.2 M / yr |
| Default foreign-turnkey external capital | $3.95 B |
| External capital saved | $3.48 B |
| Capital + lifetime external interest saved | $7.98 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $1.16 B | $173.4 M | $982.6 M |
| Stations | $341.1 M | $68.2 M | $272.9 M |
| Depots | $8.0 M | $2.0 M | $6.0 M |
| Rolling stock | $285.6 M | $100.0 M | $185.6 M |
| Dedicated solar plants | $181.7 M | $81.8 M | $99.9 M |
| Residual train control | $10.6 M | $5.3 M | $5.3 M |
| Charging microgrids | $20.1 M | $8.0 M | $12.1 M |
| EPC / project services | $131.8 M | $19.8 M | $112.0 M |
| Shared national trainset factory | $61.2 M | $12.2 M | $49.0 M |
| **Total** | **$2.20 B** | **$470.7 M** | **$1.73 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Bamako](Bamako/README.md) | 2,929,000 | 255 | $2.13 B | $457.8 M | $1.67 B |

## Local Basis And Regeneration

Country finance parameters use `ML` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
