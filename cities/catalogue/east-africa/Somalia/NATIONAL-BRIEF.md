# Somalia National OpenSourceRail Strategy

This page contains only Somalia-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$3.43 B (89.0%) of external capital** and **$4.43 B of external interest**. Capital plus saved interest totals **$7.85 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 2,610,000 |
| Trainsets / vehicle modules | 139 / 556 |
| City infrastructure and fleet CAPEX | $1.64 B |
| Shared national factory | $463.5 M |
| Factory sizing basis | 556 modules for Mogadishu, then reused nationally |
| **Total national programme** | **$2.14 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $423.8 M (19.8%) |
| Domestic / local capital | $1.72 B (80.2%) |
| Annual external capital draw | $42.4 M / yr |
| Annual local capital draw | $171.5 M / yr |
| Annual public construction commitment | $259.2 M / yr for 10 years |
| Annual post-grace debt service | $235.0 M / yr |
| Default foreign-turnkey external capital | $3.85 B |
| External capital saved | $3.43 B |
| Capital + lifetime external interest saved | $7.85 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $994.1 M | $149.1 M | $845.0 M |
| Stations | $214.8 M | $43.0 M | $171.8 M |
| Depots | $73.3 M | $18.3 M | $55.0 M |
| Rolling stock | $155.7 M | $54.5 M | $101.2 M |
| Dedicated solar plants | $84.4 M | $38.0 M | $46.4 M |
| Residual train control | $5.7 M | $2.9 M | $2.9 M |
| Charging microgrids | $13.1 M | $5.2 M | $7.8 M |
| EPC / project services | $134.4 M | $20.2 M | $114.2 M |
| Shared national trainset factory | $463.5 M | $92.7 M | $370.8 M |
| **Total** | **$2.14 B** | **$423.8 M** | **$1.72 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Mogadishu](Mogadishu/README.md) | 2,610,000 | 139 | $1.64 B | $326.2 M | $1.32 B |

## Local Basis And Regeneration

Country finance parameters use `SO` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
