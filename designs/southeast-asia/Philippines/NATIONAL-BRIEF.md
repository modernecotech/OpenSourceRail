# Philippines National OpenSourceRail Strategy

This page contains only Philippines-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$3.56 B (86.5%) of external capital** and **$4.38 B of external interest**. Capital plus saved interest totals **$7.94 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 1,827,000 |
| Trainsets / vehicle modules | 329 / 1,316 |
| City infrastructure and fleet CAPEX | $2.20 B |
| Shared national factory | $79.0 M |
| Factory sizing basis | 1,316 modules for Davao, then reused nationally |
| **Total national programme** | **$2.29 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $557.7 M (24.4%) |
| Domestic / local capital | $1.73 B (75.6%) |
| Annual external capital draw | $111.5 M / yr |
| Annual local capital draw | $346.0 M / yr |
| Annual public construction commitment | $180.1 M / yr for 5 years |
| Annual post-grace debt service | $129.7 M / yr |
| Default foreign-turnkey external capital | $4.12 B |
| External capital saved | $3.56 B |
| Capital + lifetime external interest saved | $7.94 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $858.7 M | $128.8 M | $729.9 M |
| Stations | $467.7 M | $93.5 M | $374.2 M |
| Depots | $8.0 M | $2.0 M | $6.0 M |
| Rolling stock | $368.5 M | $129.0 M | $239.5 M |
| Dedicated solar plants | $334.6 M | $150.6 M | $184.0 M |
| Residual train control | $14.0 M | $7.0 M | $7.0 M |
| Charging microgrids | $29.7 M | $11.9 M | $17.8 M |
| EPC / project services | $127.8 M | $19.2 M | $108.6 M |
| Shared national trainset factory | $79.0 M | $15.8 M | $63.2 M |
| **Total** | **$2.29 B** | **$557.7 M** | **$1.73 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Davao](Davao/README.md) | 1,827,000 | 329 | $2.20 B | $541.1 M | $1.66 B |

## Local Basis And Regeneration

Country finance parameters use `PH` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 scripts/generate-national-briefs.py
```
