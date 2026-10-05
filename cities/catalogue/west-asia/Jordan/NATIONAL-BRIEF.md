# Jordan National OpenSourceRail Strategy

This page contains only Jordan-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$16.92 B (88.8%) of external capital** and **$20.80 B of external interest**. Capital plus saved interest totals **$37.71 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 4 |
| Represented population | 5,557,000 |
| Trainsets / vehicle modules | 920 / 4,258 |
| City infrastructure and fleet CAPEX | $9.93 B |
| Shared national factory | $607.5 M |
| Factory sizing basis | 3,138 modules for Amman, then reused nationally |
| **Total national programme** | **$10.58 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $2.13 B (20.1%) |
| Domestic / local capital | $8.45 B (79.9%) |
| Annual external capital draw | $425.4 M / yr |
| Annual local capital draw | $1.69 B / yr |
| Annual public construction commitment | $940.9 M / yr for 5 years |
| Annual post-grace debt service | $672.8 M / yr |
| Default foreign-turnkey external capital | $19.04 B |
| External capital saved | $16.92 B |
| Capital + lifetime external interest saved | $37.71 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $6.05 B | $907.0 M | $5.14 B |
| Stations | $1.07 B | $213.2 M | $853.0 M |
| Depots | $402.9 M | $100.7 M | $302.2 M |
| Rolling stock | $1.21 B | $424.1 M | $787.7 M |
| Dedicated solar plants | $504.5 M | $227.0 M | $277.5 M |
| Residual train control | $22.7 M | $11.3 M | $11.3 M |
| Charging microgrids | $58.0 M | $23.2 M | $34.8 M |
| EPC / project services | $659.1 M | $98.9 M | $560.2 M |
| Shared national trainset factory | $607.5 M | $121.5 M | $486.0 M |
| **Total** | **$10.58 B** | **$2.13 B** | **$8.45 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Amman](Amman/README.md) | 4,007,000 | 523 | $5.50 B | $1.21 B | $4.29 B |
| [Zarqa](Zarqa/README.md) | 700,000 | 205 | $1.26 B | $252.4 M | $1.00 B |
| [Irbid](Irbid/README.md) | 600,000 | 121 | $666.6 M | $138.8 M | $527.8 M |
| [Aqaba](Aqaba/README.md) | 250,000 | 71 | $2.50 B | $394.1 M | $2.11 B |

## Local Basis And Regeneration

Country finance parameters use `JO` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
