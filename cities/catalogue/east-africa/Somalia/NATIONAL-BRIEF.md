# Somalia National OpenSourceRail Strategy

This page contains only Somalia-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$4.80 B (89.9%) of external capital** and **$6.20 B of external interest**. Capital plus saved interest totals **$11.00 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 2,610,000 |
| Trainsets / vehicle modules | 132 / 528 |
| City infrastructure and fleet CAPEX | $2.49 B |
| Shared national factory | $446.5 M |
| Factory sizing basis | 528 modules for Mogadishu, then reused nationally |
| **Total national programme** | **$2.97 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $541.8 M (18.3%) |
| Domestic / local capital | $2.43 B (81.7%) |
| Annual external capital draw | $54.2 M / yr |
| Annual local capital draw | $242.6 M / yr |
| Annual public construction commitment | $364.0 M / yr for 10 years |
| Annual post-grace debt service | $328.8 M / yr |
| Default foreign-turnkey external capital | $5.34 B |
| External capital saved | $4.80 B |
| Capital + lifetime external interest saved | $11.00 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $1.84 B | $276.3 M | $1.57 B |
| Stations | $172.3 M | $34.5 M | $137.8 M |
| Depots | $72.8 M | $18.2 M | $54.6 M |
| Rolling stock | $147.8 M | $51.7 M | $96.1 M |
| Dedicated solar plants | $80.6 M | $36.3 M | $44.3 M |
| Residual train control | $5.4 M | $2.7 M | $2.7 M |
| Charging microgrids | $11.2 M | $4.5 M | $6.8 M |
| EPC / project services | $188.9 M | $28.3 M | $160.5 M |
| Shared national trainset factory | $446.5 M | $89.3 M | $357.2 M |
| **Total** | **$2.97 B** | **$541.8 M** | **$2.43 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Mogadishu](Mogadishu/README.md) | 2,610,000 | 132 | $2.49 B | $447.8 M | $2.04 B |

## Local Basis And Regeneration

Country finance parameters use `SO` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
