# Indonesia National OpenSourceRail Strategy

This page contains only Indonesia-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$15.98 B (87.9%) of external capital** and **$19.64 B of external interest**. Capital plus saved interest totals **$35.62 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 2 |
| Represented population | 5,624,000 |
| Trainsets / vehicle modules | 889 / 4,644 |
| City infrastructure and fleet CAPEX | $9.64 B |
| Shared national factory | $425.5 M |
| Factory sizing basis | 3,264 modules for Surabaya, then reused nationally |
| **Total national programme** | **$10.10 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $2.19 B (21.7%) |
| Domestic / local capital | $7.90 B (78.3%) |
| Annual external capital draw | $438.9 M / yr |
| Annual local capital draw | $1.58 B / yr |
| Annual public construction commitment | $838.3 M / yr for 5 years |
| Annual post-grace debt service | $598.0 M / yr |
| Default foreign-turnkey external capital | $18.17 B |
| External capital saved | $15.98 B |
| Capital + lifetime external interest saved | $35.62 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $4.48 B | $672.0 M | $3.81 B |
| Stations | $2.02 B | $403.5 M | $1.61 B |
| Depots | $383.1 M | $95.8 M | $287.3 M |
| Rolling stock | $1.30 B | $455.1 M | $845.2 M |
| Dedicated solar plants | $752.6 M | $338.6 M | $413.9 M |
| Residual train control | $25.5 M | $12.8 M | $12.8 M |
| Charging microgrids | $99.8 M | $39.9 M | $59.9 M |
| EPC / project services | $611.2 M | $91.7 M | $519.5 M |
| Shared national trainset factory | $425.5 M | $85.1 M | $340.4 M |
| **Total** | **$10.10 B** | **$2.19 B** | **$7.90 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Surabaya](Surabaya/README.md) | 3,009,000 | 544 | $5.84 B | $1.31 B | $4.52 B |
| [Bandung](Bandung/README.md) | 2,615,000 | 345 | $3.80 B | $792.6 M | $3.01 B |

## Local Basis And Regeneration

Country finance parameters use `ID` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
