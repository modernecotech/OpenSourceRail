# Ecuador National OpenSourceRail Strategy

This page contains only Ecuador-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$2.40 B (88.4%) of external capital** and **$2.95 B of external interest**. Capital plus saved interest totals **$5.35 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 817,100 |
| Trainsets / vehicle modules | 188 / 564 |
| City infrastructure and fleet CAPEX | $910.0 M |
| Shared national factory | $559.9 M |
| Factory sizing basis | 564 modules for Cuenca, then reused nationally |
| **Total national programme** | **$1.51 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $315.4 M (20.9%) |
| Domestic / local capital | $1.19 B (79.1%) |
| Annual external capital draw | $63.1 M / yr |
| Annual local capital draw | $238.7 M / yr |
| Annual public construction commitment | $152.7 M / yr for 5 years |
| Annual post-grace debt service | $112.7 M / yr |
| Default foreign-turnkey external capital | $2.72 B |
| External capital saved | $2.40 B |
| Capital + lifetime external interest saved | $5.35 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $484.3 M | $72.7 M | $411.7 M |
| Stations | $81.9 M | $16.4 M | $65.5 M |
| Depots | $62.3 M | $15.6 M | $46.7 M |
| Rolling stock | $169.2 M | $59.2 M | $110.0 M |
| Dedicated solar plants | $51.2 M | $23.0 M | $28.1 M |
| Residual train control | $3.0 M | $1.5 M | $1.5 M |
| Charging microgrids | $1.9 M | $780 k | $1.2 M |
| EPC / project services | $95.4 M | $14.3 M | $81.1 M |
| Shared national trainset factory | $559.9 M | $112.0 M | $447.9 M |
| **Total** | **$1.51 B** | **$315.4 M** | **$1.19 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Cuenca](Cuenca/README.md) | 817,100 | 188 | $910.0 M | $197.5 M | $712.5 M |

## Local Basis And Regeneration

Country finance parameters use `EC` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
