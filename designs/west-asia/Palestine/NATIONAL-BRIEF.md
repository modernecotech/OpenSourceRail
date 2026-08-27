# Palestine National OpenSourceRail Strategy

This page contains only Palestine-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$2.17 B (86.3%) of external capital** and **$2.73 B of external interest**. Capital plus saved interest totals **$4.90 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 3 |
| Represented population | 1,850,000 |
| Trainsets / vehicle modules | 385 / 1,155 |
| City infrastructure and fleet CAPEX | $1.37 B |
| Shared national factory | $31.3 M |
| Factory sizing basis | 522 modules for Nablus, then reused nationally |
| **Total national programme** | **$1.40 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $344.3 M (24.6%) |
| Domestic / local capital | $1.06 B (75.4%) |
| Annual external capital draw | $49.2 M / yr |
| Annual local capital draw | $150.7 M / yr |
| Annual public construction commitment | $117.4 M / yr for 7 years |
| Annual post-grace debt service | $97.2 M / yr |
| Default foreign-turnkey external capital | $2.52 B |
| External capital saved | $2.17 B |
| Capital + lifetime external interest saved | $4.90 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $491.6 M | $73.7 M | $417.8 M |
| Stations | $264.8 M | $53.0 M | $211.8 M |
| Depots | $24.0 M | $6.0 M | $18.0 M |
| Rolling stock | $346.5 M | $121.3 M | $225.2 M |
| Dedicated solar plants | $144.7 M | $65.1 M | $79.6 M |
| Residual train control | $8.5 M | $4.3 M | $4.3 M |
| Charging microgrids | $6.0 M | $2.4 M | $3.6 M |
| EPC / project services | $82.1 M | $12.3 M | $69.8 M |
| Shared national trainset factory | $31.3 M | $6.3 M | $25.1 M |
| **Total** | **$1.40 B** | **$344.3 M** | **$1.06 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Hebron](Hebron/README.md) | 800,000 | 127 | $478.0 M | $117.3 M | $360.7 M |
| [Gaza City](Gaza-City/README.md) | 600,000 | 84 | $331.5 M | $79.6 M | $251.9 M |
| [Nablus](Nablus/README.md) | 450,000 | 174 | $556.4 M | $140.8 M | $415.6 M |

## Local Basis And Regeneration

Country finance parameters use `PS` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 scripts/generate-national-briefs.py
```
