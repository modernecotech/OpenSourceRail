# Cambodia National OpenSourceRail Strategy

This page contains only Cambodia-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$3.75 B (87.3%) of external capital** and **$4.71 B of external interest**. Capital plus saved interest totals **$8.46 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 2,281,000 |
| Trainsets / vehicle modules | 293 / 1,172 |
| City infrastructure and fleet CAPEX | $2.31 B |
| Shared national factory | $70.3 M |
| Factory sizing basis | 1,172 modules for Phnom Penh, then reused nationally |
| **Total national programme** | **$2.39 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $548.1 M (22.9%) |
| Domestic / local capital | $1.84 B (77.1%) |
| Annual external capital draw | $78.3 M / yr |
| Annual local capital draw | $263.1 M / yr |
| Annual public construction commitment | $195.2 M / yr for 7 years |
| Annual post-grace debt service | $160.2 M / yr |
| Default foreign-turnkey external capital | $4.30 B |
| External capital saved | $3.75 B |
| Capital + lifetime external interest saved | $8.46 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $1.06 B | $159.4 M | $903.4 M |
| Stations | $459.3 M | $91.9 M | $367.4 M |
| Depots | $8.0 M | $2.0 M | $6.0 M |
| Rolling stock | $328.2 M | $114.9 M | $213.3 M |
| Dedicated solar plants | $289.8 M | $130.4 M | $159.4 M |
| Residual train control | $11.9 M | $6.0 M | $6.0 M |
| Charging microgrids | $22.3 M | $8.9 M | $13.4 M |
| EPC / project services | $137.4 M | $20.6 M | $116.8 M |
| Shared national trainset factory | $70.3 M | $14.1 M | $56.3 M |
| **Total** | **$2.39 B** | **$548.1 M** | **$1.84 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Phnom Penh](Phnom-Penh/README.md) | 2,281,000 | 293 | $2.31 B | $533.3 M | $1.78 B |

## Local Basis And Regeneration

Country finance parameters use `KH` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 scripts/generate-national-briefs.py
```
