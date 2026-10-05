# Niger National OpenSourceRail Strategy

This page contains only Niger-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$4.48 B (89.2%) of external capital** and **$5.78 B of external interest**. Capital plus saved interest totals **$10.26 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 1,407,635 |
| Trainsets / vehicle modules | 178 / 712 |
| City infrastructure and fleet CAPEX | $2.17 B |
| Shared national factory | $573.3 M |
| Factory sizing basis | 712 modules for Niamey, then reused nationally |
| **Total national programme** | **$2.79 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $543.2 M (19.5%) |
| Domestic / local capital | $2.25 B (80.5%) |
| Annual external capital draw | $54.3 M / yr |
| Annual local capital draw | $224.5 M / yr |
| Annual public construction commitment | $231.0 M / yr for 10 years |
| Annual post-grace debt service | $208.2 M / yr |
| Default foreign-turnkey external capital | $5.02 B |
| External capital saved | $4.48 B |
| Capital + lifetime external interest saved | $10.26 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $1.38 B | $207.4 M | $1.18 B |
| Stations | $238.2 M | $47.6 M | $190.6 M |
| Depots | $102.7 M | $25.7 M | $77.0 M |
| Rolling stock | $199.4 M | $69.8 M | $129.6 M |
| Dedicated solar plants | $93.2 M | $42.0 M | $51.3 M |
| Residual train control | $7.1 M | $3.5 M | $3.5 M |
| Charging microgrids | $15.2 M | $6.1 M | $9.1 M |
| EPC / project services | $176.3 M | $26.4 M | $149.9 M |
| Shared national trainset factory | $573.3 M | $114.7 M | $458.6 M |
| **Total** | **$2.79 B** | **$543.2 M** | **$2.25 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Niamey](Niamey/README.md) | 1,407,635 | 178 | $2.17 B | $422.5 M | $1.75 B |

## Local Basis And Regeneration

Country finance parameters use `NE` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
