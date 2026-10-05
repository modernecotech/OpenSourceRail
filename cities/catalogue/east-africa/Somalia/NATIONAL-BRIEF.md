# Somalia National OpenSourceRail Strategy

This page contains only Somalia-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$36.40 B (91.4%) of external capital** and **$47.02 B of external interest**. Capital plus saved interest totals **$83.42 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 2,610,000 |
| Trainsets / vehicle modules | 139 / 556 |
| City infrastructure and fleet CAPEX | $21.63 B |
| Shared national factory | $463.5 M |
| Factory sizing basis | 556 modules for Mogadishu, then reused nationally |
| **Total national programme** | **$22.12 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $3.42 B (15.5%) |
| Domestic / local capital | $18.70 B (84.5%) |
| Annual external capital draw | $342.1 M / yr |
| Annual local capital draw | $1.87 B / yr |
| Annual public construction commitment | $2.77 B / yr for 10 years |
| Annual post-grace debt service | $2.49 B / yr |
| Default foreign-turnkey external capital | $39.82 B |
| External capital saved | $36.40 B |
| Capital + lifetime external interest saved | $83.42 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $19.67 B | $2.95 B | $16.72 B |
| Stations | $214.8 M | $43.0 M | $171.8 M |
| Depots | $73.3 M | $18.3 M | $55.0 M |
| Rolling stock | $155.7 M | $54.5 M | $101.2 M |
| Dedicated solar plants | $84.4 M | $38.0 M | $46.4 M |
| Residual train control | $5.7 M | $2.9 M | $2.9 M |
| Charging microgrids | $13.1 M | $5.2 M | $7.8 M |
| EPC / project services | $1.44 B | $216.3 M | $1.23 B |
| Shared national trainset factory | $463.5 M | $92.7 M | $370.8 M |
| **Total** | **$22.12 B** | **$3.42 B** | **$18.70 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Mogadishu](Mogadishu/README.md) | 2,610,000 | 139 | $21.63 B | $3.32 B | $18.30 B |

## Local Basis And Regeneration

Country finance parameters use `SO` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
