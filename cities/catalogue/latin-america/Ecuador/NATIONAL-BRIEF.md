# Ecuador National OpenSourceRail Strategy

This page contains only Ecuador-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$2.36 B (88.4%) of external capital** and **$2.90 B of external interest**. Capital plus saved interest totals **$5.26 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 817,100 |
| Trainsets / vehicle modules | 185 / 555 |
| City infrastructure and fleet CAPEX | $889.1 M |
| Shared national factory | $554.0 M |
| Factory sizing basis | 555 modules for Cuenca, then reused nationally |
| **Total national programme** | **$1.48 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $309.5 M (20.9%) |
| Domestic / local capital | $1.17 B (79.1%) |
| Annual external capital draw | $61.9 M / yr |
| Annual local capital draw | $234.5 M / yr |
| Annual public construction commitment | $149.9 M / yr for 5 years |
| Annual post-grace debt service | $110.7 M / yr |
| Default foreign-turnkey external capital | $2.67 B |
| External capital saved | $2.36 B |
| Capital + lifetime external interest saved | $5.26 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $480.5 M | $72.1 M | $408.4 M |
| Stations | $70.4 M | $14.1 M | $56.3 M |
| Depots | $62.1 M | $15.5 M | $46.6 M |
| Rolling stock | $166.5 M | $58.3 M | $108.2 M |
| Dedicated solar plants | $49.9 M | $22.4 M | $27.4 M |
| Residual train control | $2.9 M | $1.5 M | $1.5 M |
| Charging microgrids | $1.9 M | $740 k | $1.1 M |
| EPC / project services | $93.7 M | $14.1 M | $79.6 M |
| Shared national trainset factory | $554.0 M | $110.8 M | $443.2 M |
| **Total** | **$1.48 B** | **$309.5 M** | **$1.17 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Cuenca](Cuenca/README.md) | 817,100 | 185 | $889.1 M | $192.8 M | $696.2 M |

## Local Basis And Regeneration

Country finance parameters use `EC` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
