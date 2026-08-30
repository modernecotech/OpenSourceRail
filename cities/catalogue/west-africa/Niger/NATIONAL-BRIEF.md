# Niger National OpenSourceRail Strategy

This page contains only Niger-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$2.17 B (87.3%) of external capital** and **$2.80 B of external interest**. Capital plus saved interest totals **$4.97 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 1,407,635 |
| Trainsets / vehicle modules | 186 / 744 |
| City infrastructure and fleet CAPEX | $1.33 B |
| Shared national factory | $44.6 M |
| Factory sizing basis | 744 modules for Niamey, then reused nationally |
| **Total national programme** | **$1.38 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $314.0 M (22.8%) |
| Domestic / local capital | $1.06 B (77.2%) |
| Annual external capital draw | $31.4 M / yr |
| Annual local capital draw | $106.5 M / yr |
| Annual public construction commitment | $112.1 M / yr for 10 years |
| Annual post-grace debt service | $102.2 M / yr |
| Default foreign-turnkey external capital | $2.48 B |
| External capital saved | $2.17 B |
| Capital + lifetime external interest saved | $4.97 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $553.7 M | $83.1 M | $470.6 M |
| Stations | $327.0 M | $65.4 M | $261.6 M |
| Depots | $8.0 M | $2.0 M | $6.0 M |
| Rolling stock | $208.3 M | $72.9 M | $135.4 M |
| Dedicated solar plants | $129.6 M | $58.3 M | $71.3 M |
| Residual train control | $7.9 M | $3.9 M | $3.9 M |
| Charging microgrids | $17.9 M | $7.2 M | $10.8 M |
| EPC / project services | $81.7 M | $12.3 M | $69.5 M |
| Shared national trainset factory | $44.6 M | $8.9 M | $35.7 M |
| **Total** | **$1.38 B** | **$314.0 M** | **$1.06 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Niamey](Niamey/README.md) | 1,407,635 | 186 | $1.33 B | $304.6 M | $1.03 B |

## Local Basis And Regeneration

Country finance parameters use `NE` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
