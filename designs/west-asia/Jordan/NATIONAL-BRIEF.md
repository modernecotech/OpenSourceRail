# Jordan National OpenSourceRail Strategy

This page contains only Jordan-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$8.36 B (86.1%) of external capital** and **$10.27 B of external interest**. Capital plus saved interest totals **$18.63 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 4 |
| Represented population | 5,557,000 |
| Trainsets / vehicle modules | 960 / 4,474 |
| City infrastructure and fleet CAPEX | $5.18 B |
| Shared national factory | $199.8 M |
| Factory sizing basis | 3,330 modules for Amman, then reused nationally |
| **Total national programme** | **$5.39 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.35 B (25.0%) |
| Domestic / local capital | $4.04 B (75.0%) |
| Annual external capital draw | $269.3 M / yr |
| Annual local capital draw | $808.8 M / yr |
| Annual public construction commitment | $465.0 M / yr for 5 years |
| Annual post-grace debt service | $340.7 M / yr |
| Default foreign-turnkey external capital | $9.70 B |
| External capital saved | $8.36 B |
| Capital + lifetime external interest saved | $18.63 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $1.84 B | $276.7 M | $1.57 B |
| Stations | $990.2 M | $198.0 M | $792.2 M |
| Depots | $32.0 M | $8.0 M | $24.0 M |
| Rolling stock | $1.27 B | $445.5 M | $827.3 M |
| Dedicated solar plants | $659.9 M | $297.0 M | $363.0 M |
| Residual train control | $25.7 M | $12.9 M | $12.9 M |
| Charging microgrids | $55.8 M | $22.3 M | $33.5 M |
| EPC / project services | $309.5 M | $46.4 M | $263.1 M |
| Shared national trainset factory | $199.8 M | $40.0 M | $159.8 M |
| **Total** | **$5.39 B** | **$1.35 B** | **$4.04 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Amman](Amman/README.md) | 4,007,000 | 555 | $3.77 B | $972.8 M | $2.80 B |
| [Zarqa](Zarqa/README.md) | 700,000 | 227 | $721.2 M | $173.6 M | $547.6 M |
| [Irbid](Irbid/README.md) | 600,000 | 107 | $380.6 M | $94.4 M | $286.2 M |
| [Aqaba](Aqaba/README.md) | 250,000 | 71 | $301.1 M | $63.9 M | $237.3 M |

## Local Basis And Regeneration

Country finance parameters use `JO` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 scripts/generate-national-briefs.py
```
