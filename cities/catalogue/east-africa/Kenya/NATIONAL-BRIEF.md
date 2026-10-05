# Kenya National OpenSourceRail Strategy

This page contains only Kenya-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$32.07 B (88.3%) of external capital** and **$40.20 B of external interest**. Capital plus saved interest totals **$72.28 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 15 |
| Represented population | 11,750,000 |
| Trainsets / vehicle modules | 2,343 / 9,093 |
| City infrastructure and fleet CAPEX | $19.51 B |
| Shared national factory | $635.0 M |
| Factory sizing basis | 4,446 modules for Nairobi, then reused nationally |
| **Total national programme** | **$20.19 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $4.27 B (21.1%) |
| Domestic / local capital | $15.92 B (78.9%) |
| Annual external capital draw | $609.8 M / yr |
| Annual local capital draw | $2.27 B / yr |
| Annual public construction commitment | $2.11 B / yr for 7 years |
| Annual post-grace debt service | $1.76 B / yr |
| Default foreign-turnkey external capital | $36.34 B |
| External capital saved | $32.07 B |
| Capital + lifetime external interest saved | $72.28 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $10.43 B | $1.56 B | $8.86 B |
| Stations | $2.75 B | $549.1 M | $2.20 B |
| Depots | $1.06 B | $264.3 M | $792.8 M |
| Rolling stock | $2.59 B | $905.4 M | $1.68 B |
| Dedicated solar plants | $1.32 B | $594.9 M | $727.1 M |
| Residual train control | $59.7 M | $29.9 M | $29.9 M |
| Charging microgrids | $123.0 M | $49.2 M | $73.8 M |
| EPC / project services | $1.23 B | $185.1 M | $1.05 B |
| Shared national trainset factory | $635.0 M | $127.0 M | $508.0 M |
| **Total** | **$20.19 B** | **$4.27 B** | **$15.92 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Nairobi](Nairobi/README.md) | 5,700,000 | 741 | $7.61 B | $1.74 B | $5.87 B |
| [Mombasa](Mombasa/README.md) | 1,350,000 | 382 | $4.56 B | $930.6 M | $3.63 B |
| [Nakuru](Nakuru/README.md) | 700,000 | 152 | $754.6 M | $158.8 M | $595.8 M |
| [Kisumu](Kisumu/README.md) | 600,000 | 141 | $776.9 M | $163.1 M | $613.8 M |
| [Eldoret](Eldoret/README.md) | 500,000 | 171 | $842.4 M | $177.7 M | $664.7 M |
| [Thika](Thika/README.md) | 350,000 | 215 | $1.02 B | $223.4 M | $800.9 M |
| [Garissa](Garissa/README.md) | 300,000 | 44 | $296.4 M | $56.4 M | $240.0 M |
| [Kakamega](Kakamega/README.md) | 300,000 | 80 | $558.0 M | $106.2 M | $451.8 M |
| [Kisii](Kisii/README.md) | 300,000 | 45 | $297.9 M | $56.9 M | $241.0 M |
| [Kitale](Kitale/README.md) | 300,000 | 75 | $530.2 M | $101.0 M | $429.1 M |
| [Machakos](Machakos/README.md) | 300,000 | 50 | $354.7 M | $66.5 M | $288.2 M |
| [Malindi](Malindi/README.md) | 300,000 | 53 | $373.7 M | $70.3 M | $303.4 M |
| [Meru Ke](Meru-Ke/README.md) | 250,000 | 51 | $407.0 M | $74.1 M | $332.8 M |
| [Naivasha](Naivasha/README.md) | 250,000 | 76 | $528.2 M | $98.9 M | $429.2 M |
| [Nyeri](Nyeri/README.md) | 250,000 | 67 | $590.8 M | $107.3 M | $483.5 M |

## Local Basis And Regeneration

Country finance parameters use `KE` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
