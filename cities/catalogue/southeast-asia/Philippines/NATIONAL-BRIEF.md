# Philippines National OpenSourceRail Strategy

This page contains only Philippines-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$6.93 B (88.4%) of external capital** and **$8.53 B of external interest**. Capital plus saved interest totals **$15.46 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 1,827,000 |
| Trainsets / vehicle modules | 358 / 1,432 |
| City infrastructure and fleet CAPEX | $3.85 B |
| Shared national factory | $467.9 M |
| Factory sizing basis | 1,432 modules for Davao, then reused nationally |
| **Total national programme** | **$4.36 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $905.7 M (20.8%) |
| Domestic / local capital | $3.45 B (79.2%) |
| Annual external capital draw | $181.1 M / yr |
| Annual local capital draw | $690.0 M / yr |
| Annual public construction commitment | $349.9 M / yr for 5 years |
| Annual post-grace debt service | $246.7 M / yr |
| Default foreign-turnkey external capital | $7.84 B |
| External capital saved | $6.93 B |
| Capital + lifetime external interest saved | $15.46 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $2.08 B | $311.7 M | $1.77 B |
| Stations | $659.9 M | $132.0 M | $527.9 M |
| Depots | $140.9 M | $35.2 M | $105.7 M |
| Rolling stock | $401.0 M | $140.3 M | $260.6 M |
| Dedicated solar plants | $294.4 M | $132.5 M | $161.9 M |
| Residual train control | $13.5 M | $6.8 M | $6.8 M |
| Charging microgrids | $34.5 M | $13.8 M | $20.7 M |
| EPC / project services | $265.7 M | $39.9 M | $225.8 M |
| Shared national trainset factory | $467.9 M | $93.6 M | $374.3 M |
| **Total** | **$4.36 B** | **$905.7 M** | **$3.45 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Davao](Davao/README.md) | 1,827,000 | 358 | $3.85 B | $807.2 M | $3.05 B |

## Local Basis And Regeneration

Country finance parameters use `PH` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
