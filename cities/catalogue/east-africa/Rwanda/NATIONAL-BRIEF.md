# Rwanda National OpenSourceRail Strategy

This page contains only Rwanda-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$6.74 B (88.9%) of external capital** and **$8.45 B of external interest**. Capital plus saved interest totals **$15.18 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 3 |
| Represented population | 1,708,000 |
| Trainsets / vehicle modules | 369 / 1,158 |
| City infrastructure and fleet CAPEX | $3.50 B |
| Shared national factory | $664.9 M |
| Factory sizing basis | 840 modules for Kigali, then reused nationally |
| **Total national programme** | **$4.21 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $839.8 M (20.0%) |
| Domestic / local capital | $3.37 B (80.0%) |
| Annual external capital draw | $120.0 M / yr |
| Annual local capital draw | $481.4 M / yr |
| Annual public construction commitment | $363.2 M / yr for 7 years |
| Annual post-grace debt service | $295.1 M / yr |
| Default foreign-turnkey external capital | $7.58 B |
| External capital saved | $6.74 B |
| Capital + lifetime external interest saved | $15.18 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $2.01 B | $301.3 M | $1.71 B |
| Stations | $534.0 M | $106.8 M | $427.2 M |
| Depots | $199.9 M | $50.0 M | $149.9 M |
| Rolling stock | $324.2 M | $113.5 M | $210.8 M |
| Dedicated solar plants | $179.7 M | $80.8 M | $98.8 M |
| Residual train control | $11.6 M | $5.8 M | $5.8 M |
| Charging microgrids | $22.6 M | $9.0 M | $13.5 M |
| EPC / project services | $263.6 M | $39.5 M | $224.1 M |
| Shared national trainset factory | $664.9 M | $133.0 M | $531.9 M |
| **Total** | **$4.21 B** | **$839.8 M** | **$3.37 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Kigali](Kigali/README.md) | 1,208,000 | 210 | $2.49 B | $504.5 M | $1.98 B |
| [Huye](Huye/README.md) | 250,000 | 83 | $509.3 M | $98.9 M | $410.4 M |
| [Rubavu](Rubavu/README.md) | 250,000 | 76 | $502.0 M | $96.5 M | $405.5 M |

## Local Basis And Regeneration

Country finance parameters use `RW` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
