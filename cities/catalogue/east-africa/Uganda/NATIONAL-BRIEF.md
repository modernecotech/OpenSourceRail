# Uganda National OpenSourceRail Strategy

This page contains only Uganda-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$14.55 B (88.9%) of external capital** and **$18.24 B of external interest**. Capital plus saved interest totals **$32.79 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 12 |
| Represented population | 4,925,000 |
| Trainsets / vehicle modules | 1,121 / 3,048 |
| City infrastructure and fleet CAPEX | $8.29 B |
| Shared national factory | $753.9 M |
| Factory sizing basis | 968 modules for Kampala, then reused nationally |
| **Total national programme** | **$9.09 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.82 B (20.0%) |
| Domestic / local capital | $7.28 B (80.0%) |
| Annual external capital draw | $259.6 M / yr |
| Annual local capital draw | $1.04 B / yr |
| Annual public construction commitment | $1.10 B / yr for 7 years |
| Annual post-grace debt service | $932.5 M / yr |
| Default foreign-turnkey external capital | $16.37 B |
| External capital saved | $14.55 B |
| Capital + lifetime external interest saved | $32.79 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $4.69 B | $703.8 M | $3.99 B |
| Stations | $1.19 B | $238.3 M | $953.4 M |
| Depots | $603.5 M | $150.9 M | $452.6 M |
| Rolling stock | $872.8 M | $305.5 M | $567.3 M |
| Dedicated solar plants | $342.4 M | $154.1 M | $188.3 M |
| Residual train control | $27.3 M | $13.6 M | $13.6 M |
| Charging microgrids | $36.6 M | $14.6 M | $22.0 M |
| EPC / project services | $572.4 M | $85.9 M | $486.6 M |
| Shared national trainset factory | $753.9 M | $150.8 M | $603.2 M |
| **Total** | **$9.09 B** | **$1.82 B** | **$7.28 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Kampala](Kampala/README.md) | 1,875,000 | 242 | $2.72 B | $559.2 M | $2.16 B |
| [Mbarara](Mbarara/README.md) | 500,000 | 150 | $833.7 M | $174.7 M | $658.9 M |
| [Gulu](Gulu/README.md) | 350,000 | 172 | $857.6 M | $185.2 M | $672.5 M |
| [Jinja](Jinja/README.md) | 300,000 | 90 | $632.2 M | $121.3 M | $510.8 M |
| [Mbale](Mbale/README.md) | 300,000 | 51 | $401.7 M | $74.0 M | $327.7 M |
| [Arua](Arua/README.md) | 250,000 | 68 | $487.2 M | $92.6 M | $394.5 M |
| [Entebbe](Entebbe/README.md) | 250,000 | 72 | $511.4 M | $98.0 M | $413.4 M |
| [Lira](Lira/README.md) | 250,000 | 80 | $500.9 M | $97.0 M | $404.0 M |
| [Masaka](Masaka/README.md) | 250,000 | 61 | $430.1 M | $81.3 M | $348.8 M |
| [Fort Portal](Fort-Portal/README.md) | 200,000 | 64 | $446.0 M | $84.8 M | $361.2 M |
| [Hoima](Hoima/README.md) | 200,000 | 54 | $358.7 M | $68.6 M | $290.1 M |
| [Soroti](Soroti/README.md) | 200,000 | 17 | $110.0 M | $22.1 M | $87.9 M |

## Local Basis And Regeneration

Country finance parameters use `UG` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
