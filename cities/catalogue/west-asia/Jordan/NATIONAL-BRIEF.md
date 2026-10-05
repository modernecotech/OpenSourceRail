# Jordan National OpenSourceRail Strategy

This page contains only Jordan-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$13.44 B (88.1%) of external capital** and **$16.52 B of external interest**. Capital plus saved interest totals **$29.95 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 4 |
| Represented population | 5,557,000 |
| Trainsets / vehicle modules | 920 / 4,258 |
| City infrastructure and fleet CAPEX | $7.82 B |
| Shared national factory | $607.5 M |
| Factory sizing basis | 3,138 modules for Amman, then reused nationally |
| **Total national programme** | **$8.47 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.81 B (21.4%) |
| Domestic / local capital | $6.66 B (78.6%) |
| Annual external capital draw | $362.1 M / yr |
| Annual local capital draw | $1.33 B / yr |
| Annual public construction commitment | $747.4 M / yr for 5 years |
| Annual post-grace debt service | $537.8 M / yr |
| Default foreign-turnkey external capital | $15.25 B |
| External capital saved | $13.44 B |
| Capital + lifetime external interest saved | $29.95 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $4.08 B | $611.3 M | $3.46 B |
| Stations | $1.07 B | $213.2 M | $853.0 M |
| Depots | $402.9 M | $100.7 M | $302.2 M |
| Rolling stock | $1.21 B | $424.1 M | $787.7 M |
| Dedicated solar plants | $504.5 M | $227.0 M | $277.5 M |
| Residual train control | $22.7 M | $11.3 M | $11.3 M |
| Charging microgrids | $58.0 M | $23.2 M | $34.8 M |
| EPC / project services | $521.1 M | $78.2 M | $443.0 M |
| Shared national trainset factory | $607.5 M | $121.5 M | $486.0 M |
| **Total** | **$8.47 B** | **$1.81 B** | **$6.66 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Amman](Amman/README.md) | 4,007,000 | 523 | $5.49 B | $1.21 B | $4.28 B |
| [Zarqa](Zarqa/README.md) | 700,000 | 205 | $1.17 B | $239.2 M | $927.9 M |
| [Irbid](Irbid/README.md) | 600,000 | 121 | $664.5 M | $138.5 M | $526.0 M |
| [Aqaba](Aqaba/README.md) | 250,000 | 71 | $495.9 M | $93.0 M | $402.9 M |

## Local Basis And Regeneration

Country finance parameters use `JO` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
