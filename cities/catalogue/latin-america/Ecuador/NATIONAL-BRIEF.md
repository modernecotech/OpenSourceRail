# Ecuador National OpenSourceRail Strategy

This page contains only Ecuador-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$902.7 M (85.9%) of external capital** and **$1.11 B of external interest**. Capital plus saved interest totals **$2.01 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 817,100 |
| Trainsets / vehicle modules | 169 / 507 |
| City infrastructure and fleet CAPEX | $551.1 M |
| Shared national factory | $30.4 M |
| Factory sizing basis | 507 modules for Cuenca, then reused nationally |
| **Total national programme** | **$583.7 M** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $148.0 M (25.3%) |
| Domestic / local capital | $435.7 M (74.7%) |
| Annual external capital draw | $29.6 M / yr |
| Annual local capital draw | $87.1 M / yr |
| Annual public construction commitment | $57.2 M / yr for 5 years |
| Annual post-grace debt service | $43.0 M / yr |
| Default foreign-turnkey external capital | $1.05 B |
| External capital saved | $902.7 M |
| Capital + lifetime external interest saved | $2.01 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $196.6 M | $29.5 M | $167.1 M |
| Stations | $85.4 M | $17.1 M | $68.3 M |
| Depots | $8.0 M | $2.0 M | $6.0 M |
| Rolling stock | $152.1 M | $53.2 M | $98.9 M |
| Dedicated solar plants | $72.0 M | $32.4 M | $39.6 M |
| Residual train control | $3.5 M | $1.8 M | $1.8 M |
| Charging microgrids | $2.1 M | $860 k | $1.3 M |
| EPC / project services | $33.5 M | $5.0 M | $28.5 M |
| Shared national trainset factory | $30.4 M | $6.1 M | $24.3 M |
| **Total** | **$583.7 M** | **$148.0 M** | **$435.7 M** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Cuenca](Cuenca/README.md) | 817,100 | 169 | $551.1 M | $141.6 M | $409.6 M |

## Local Basis And Regeneration

Country finance parameters use `EC` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
