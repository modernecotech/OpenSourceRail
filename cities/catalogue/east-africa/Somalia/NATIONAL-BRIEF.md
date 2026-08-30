# Somalia National OpenSourceRail Strategy

This page contains only Somalia-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$1.73 B (87.2%) of external capital** and **$2.23 B of external interest**. Capital plus saved interest totals **$3.96 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 2,610,000 |
| Trainsets / vehicle modules | 149 / 596 |
| City infrastructure and fleet CAPEX | $1.06 B |
| Shared national factory | $35.8 M |
| Factory sizing basis | 596 modules for Mogadishu, then reused nationally |
| **Total national programme** | **$1.10 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $253.9 M (23.0%) |
| Domestic / local capital | $848.1 M (77.0%) |
| Annual external capital draw | $25.4 M / yr |
| Annual local capital draw | $84.8 M / yr |
| Annual public construction commitment | $130.2 M / yr for 10 years |
| Annual post-grace debt service | $118.9 M / yr |
| Default foreign-turnkey external capital | $1.98 B |
| External capital saved | $1.73 B |
| Capital + lifetime external interest saved | $3.96 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $401.0 M | $60.2 M | $340.9 M |
| Stations | $297.9 M | $59.6 M | $238.3 M |
| Depots | $8.0 M | $2.0 M | $6.0 M |
| Rolling stock | $166.9 M | $58.4 M | $108.5 M |
| Dedicated solar plants | $106.4 M | $47.9 M | $58.5 M |
| Residual train control | $6.0 M | $3.0 M | $3.0 M |
| Charging microgrids | $15.0 M | $6.0 M | $9.0 M |
| EPC / project services | $65.1 M | $9.8 M | $55.4 M |
| Shared national trainset factory | $35.8 M | $7.2 M | $28.6 M |
| **Total** | **$1.10 B** | **$253.9 M** | **$848.1 M** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Mogadishu](Mogadishu/README.md) | 2,610,000 | 149 | $1.06 B | $246.4 M | $817.4 M |

## Local Basis And Regeneration

Country finance parameters use `SO` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
