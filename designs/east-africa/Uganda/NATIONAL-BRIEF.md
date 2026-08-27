# Uganda National OpenSourceRail Strategy

This page contains only Uganda-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$7.98 B (86.9%) of external capital** and **$10.01 B of external interest**. Capital plus saved interest totals **$17.99 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 12 |
| Represented population | 4,925,000 |
| Trainsets / vehicle modules | 1,160 / 3,120 |
| City infrastructure and fleet CAPEX | $5.03 B |
| Shared national factory | $65.8 M |
| Factory sizing basis | 1,096 modules for Kampala, then reused nationally |
| **Total national programme** | **$5.10 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.20 B (23.5%) |
| Domestic / local capital | $3.90 B (76.5%) |
| Annual external capital draw | $171.3 M / yr |
| Annual local capital draw | $557.5 M / yr |
| Annual public construction commitment | $602.6 M / yr for 7 years |
| Annual post-grace debt service | $513.4 M / yr |
| Default foreign-turnkey external capital | $9.18 B |
| External capital saved | $7.98 B |
| Capital + lifetime external interest saved | $17.99 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $1.96 B | $293.3 M | $1.66 B |
| Stations | $1.18 B | $236.7 M | $946.6 M |
| Depots | $96.0 M | $24.0 M | $72.0 M |
| Rolling stock | $888.7 M | $311.1 M | $577.7 M |
| Dedicated solar plants | $543.0 M | $244.4 M | $298.7 M |
| Residual train control | $31.9 M | $16.0 M | $16.0 M |
| Charging microgrids | $39.8 M | $15.9 M | $23.9 M |
| EPC / project services | $298.2 M | $44.7 M | $253.5 M |
| Shared national trainset factory | $65.8 M | $13.2 M | $52.6 M |
| **Total** | **$5.10 B** | **$1.20 B** | **$3.90 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Kampala](Kampala/README.md) | 1,875,000 | 274 | $1.82 B | $444.4 M | $1.38 B |
| [Mbarara](Mbarara/README.md) | 500,000 | 113 | $454.8 M | $111.4 M | $343.4 M |
| [Gulu](Gulu/README.md) | 350,000 | 139 | $443.3 M | $115.5 M | $327.7 M |
| [Jinja](Jinja/README.md) | 300,000 | 87 | $312.4 M | $70.0 M | $242.4 M |
| [Mbale](Mbale/README.md) | 300,000 | 71 | $250.9 M | $55.3 M | $195.6 M |
| [Arua](Arua/README.md) | 250,000 | 77 | $288.9 M | $64.2 M | $224.7 M |
| [Entebbe](Entebbe/README.md) | 250,000 | 78 | $297.6 M | $66.1 M | $231.5 M |
| [Lira](Lira/README.md) | 250,000 | 92 | $321.1 M | $72.5 M | $248.6 M |
| [Masaka](Masaka/README.md) | 250,000 | 69 | $260.4 M | $57.5 M | $202.9 M |
| [Fort Portal](Fort-Portal/README.md) | 200,000 | 76 | $280.8 M | $62.5 M | $218.3 M |
| [Hoima](Hoima/README.md) | 200,000 | 61 | $202.1 M | $45.8 M | $156.3 M |
| [Soroti](Soroti/README.md) | 200,000 | 23 | $96.6 M | $20.0 M | $76.6 M |

## Local Basis And Regeneration

Country finance parameters use `UG` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 scripts/generate-national-briefs.py
```
