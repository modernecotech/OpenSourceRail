# El Salvador National OpenSourceRail Strategy

This page contains only El Salvador-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$6.65 B (88.6%) of external capital** and **$8.18 B of external interest**. Capital plus saved interest totals **$14.84 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 1,800,000 |
| Trainsets / vehicle modules | 307 / 1,228 |
| City infrastructure and fleet CAPEX | $3.49 B |
| Shared national factory | $637.1 M |
| Factory sizing basis | 1,228 modules for San Salvador, then reused nationally |
| **Total national programme** | **$4.17 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $852.4 M (20.4%) |
| Domestic / local capital | $3.32 B (79.6%) |
| Annual external capital draw | $170.5 M / yr |
| Annual local capital draw | $663.6 M / yr |
| Annual public construction commitment | $476.3 M / yr for 5 years |
| Annual post-grace debt service | $361.0 M / yr |
| Default foreign-turnkey external capital | $7.51 B |
| External capital saved | $6.65 B |
| Capital + lifetime external interest saved | $14.84 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $1.99 B | $298.7 M | $1.69 B |
| Stations | $519.6 M | $103.9 M | $415.7 M |
| Depots | $129.1 M | $32.3 M | $96.8 M |
| Rolling stock | $343.8 M | $120.3 M | $223.5 M |
| Dedicated solar plants | $256.1 M | $115.2 M | $140.8 M |
| Residual train control | $11.8 M | $5.9 M | $5.9 M |
| Charging microgrids | $25.4 M | $10.2 M | $15.3 M |
| EPC / project services | $256.1 M | $38.4 M | $217.7 M |
| Shared national trainset factory | $637.1 M | $127.4 M | $509.7 M |
| **Total** | **$4.17 B** | **$852.4 M** | **$3.32 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [San Salvador](San-Salvador/README.md) | 1,800,000 | 307 | $3.49 B | $718.3 M | $2.77 B |

## Local Basis And Regeneration

Country finance parameters use `SV` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
