# Philippines National OpenSourceRail Strategy

This page contains only Philippines-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$16.17 B (90.3%) of external capital** and **$19.88 B of external interest**. Capital plus saved interest totals **$36.05 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 1,827,000 |
| Trainsets / vehicle modules | 358 / 1,432 |
| City infrastructure and fleet CAPEX | $9.45 B |
| Shared national factory | $467.9 M |
| Factory sizing basis | 1,432 modules for Davao, then reused nationally |
| **Total national programme** | **$9.95 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.75 B (17.5%) |
| Domestic / local capital | $8.21 B (82.5%) |
| Annual external capital draw | $349.0 M / yr |
| Annual local capital draw | $1.64 B / yr |
| Annual public construction commitment | $813.9 M / yr for 5 years |
| Annual post-grace debt service | $563.5 M / yr |
| Default foreign-turnkey external capital | $17.91 B |
| External capital saved | $16.17 B |
| Capital + lifetime external interest saved | $36.05 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $7.31 B | $1.10 B | $6.21 B |
| Stations | $659.9 M | $132.0 M | $527.9 M |
| Depots | $140.9 M | $35.2 M | $105.7 M |
| Rolling stock | $401.0 M | $140.3 M | $260.6 M |
| Dedicated solar plants | $294.4 M | $132.5 M | $161.9 M |
| Residual train control | $13.5 M | $6.8 M | $6.8 M |
| Charging microgrids | $34.5 M | $13.8 M | $20.7 M |
| EPC / project services | $631.8 M | $94.8 M | $537.1 M |
| Shared national trainset factory | $467.9 M | $93.6 M | $374.3 M |
| **Total** | **$9.95 B** | **$1.75 B** | **$8.21 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Davao](Davao/README.md) | 1,827,000 | 358 | $9.45 B | $1.65 B | $7.81 B |

## Local Basis And Regeneration

Country finance parameters use `PH` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
