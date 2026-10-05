# Philippines National OpenSourceRail Strategy

This page contains only Philippines-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$7.72 B (89.1%) of external capital** and **$9.50 B of external interest**. Capital plus saved interest totals **$17.22 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 1,827,000 |
| Trainsets / vehicle modules | 305 / 1,220 |
| City infrastructure and fleet CAPEX | $4.21 B |
| Shared national factory | $569.0 M |
| Factory sizing basis | 1,220 modules for Davao, then reused nationally |
| **Total national programme** | **$4.82 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $944.0 M (19.6%) |
| Domestic / local capital | $3.87 B (80.4%) |
| Annual external capital draw | $188.8 M / yr |
| Annual local capital draw | $774.3 M / yr |
| Annual public construction commitment | $389.4 M / yr for 5 years |
| Annual post-grace debt service | $272.7 M / yr |
| Default foreign-turnkey external capital | $8.67 B |
| External capital saved | $7.72 B |
| Capital + lifetime external interest saved | $17.22 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $2.78 B | $416.3 M | $2.36 B |
| Stations | $394.7 M | $78.9 M | $315.8 M |
| Depots | $128.0 M | $32.0 M | $96.0 M |
| Rolling stock | $341.6 M | $119.6 M | $222.0 M |
| Dedicated solar plants | $272.5 M | $122.6 M | $149.9 M |
| Residual train control | $12.4 M | $6.2 M | $6.2 M |
| Charging microgrids | $25.1 M | $10.0 M | $15.0 M |
| EPC / project services | $297.2 M | $44.6 M | $252.6 M |
| Shared national trainset factory | $569.0 M | $113.8 M | $455.2 M |
| **Total** | **$4.82 B** | **$944.0 M** | **$3.87 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Davao](Davao/README.md) | 1,827,000 | 305 | $4.21 B | $824.2 M | $3.38 B |

## Local Basis And Regeneration

Country finance parameters use `PH` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
