# Indonesia National OpenSourceRail Strategy

This page contains only Indonesia-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$39.58 B (90.1%) of external capital** and **$48.66 B of external interest**. Capital plus saved interest totals **$88.23 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 2 |
| Represented population | 5,624,000 |
| Trainsets / vehicle modules | 889 / 4,644 |
| City infrastructure and fleet CAPEX | $23.94 B |
| Shared national factory | $425.5 M |
| Factory sizing basis | 3,264 modules for Surabaya, then reused nationally |
| **Total national programme** | **$24.40 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $4.34 B (17.8%) |
| Domestic / local capital | $20.06 B (82.2%) |
| Annual external capital draw | $868.0 M / yr |
| Annual local capital draw | $4.01 B / yr |
| Annual public construction commitment | $2.07 B / yr for 5 years |
| Annual post-grace debt service | $1.45 B / yr |
| Default foreign-turnkey external capital | $43.92 B |
| External capital saved | $39.58 B |
| Capital + lifetime external interest saved | $88.23 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $17.85 B | $2.68 B | $15.17 B |
| Stations | $2.02 B | $403.5 M | $1.61 B |
| Depots | $383.1 M | $95.8 M | $287.3 M |
| Rolling stock | $1.30 B | $455.1 M | $845.2 M |
| Dedicated solar plants | $752.6 M | $338.6 M | $413.9 M |
| Residual train control | $25.5 M | $12.8 M | $12.8 M |
| Charging microgrids | $99.8 M | $39.9 M | $59.9 M |
| EPC / project services | $1.55 B | $232.0 M | $1.31 B |
| Shared national trainset factory | $425.5 M | $85.1 M | $340.4 M |
| **Total** | **$24.40 B** | **$4.34 B** | **$20.06 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Surabaya](Surabaya/README.md) | 3,009,000 | 544 | $18.98 B | $3.28 B | $15.70 B |
| [Bandung](Bandung/README.md) | 2,615,000 | 345 | $4.96 B | $965.7 M | $3.99 B |

## Local Basis And Regeneration

Country finance parameters use `ID` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
