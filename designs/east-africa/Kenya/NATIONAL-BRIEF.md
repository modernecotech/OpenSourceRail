# Kenya National OpenSourceRail Strategy

This page contains only Kenya-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$17.24 B (86.1%) of external capital** and **$21.61 B of external interest**. Capital plus saved interest totals **$38.86 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 15 |
| Represented population | 11,750,000 |
| Trainsets / vehicle modules | 2,151 / 8,397 |
| City infrastructure and fleet CAPEX | $10.82 B |
| Shared national factory | $284.4 M |
| Factory sizing basis | 4,740 modules for Nairobi, then reused nationally |
| **Total national programme** | **$11.12 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $2.78 B (25.0%) |
| Domestic / local capital | $8.34 B (75.0%) |
| Annual external capital draw | $397.3 M / yr |
| Annual local capital draw | $1.19 B / yr |
| Annual public construction commitment | $1.13 B / yr for 7 years |
| Annual post-grace debt service | $952.7 M / yr |
| Default foreign-turnkey external capital | $20.02 B |
| External capital saved | $17.24 B |
| Capital + lifetime external interest saved | $38.86 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $3.89 B | $583.4 M | $3.31 B |
| Stations | $2.14 B | $427.3 M | $1.71 B |
| Depots | $120.0 M | $30.0 M | $90.0 M |
| Rolling stock | $2.38 B | $834.6 M | $1.55 B |
| Dedicated solar plants | $1.53 B | $686.7 M | $839.3 M |
| Residual train control | $59.9 M | $30.0 M | $30.0 M |
| Charging microgrids | $95.9 M | $38.4 M | $57.5 M |
| EPC / project services | $627.9 M | $94.2 M | $533.7 M |
| Shared national trainset factory | $284.4 M | $56.9 M | $227.5 M |
| **Total** | **$11.12 B** | **$2.78 B** | **$8.34 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Nairobi](Nairobi/README.md) | 5,700,000 | 790 | $5.00 B | $1.38 B | $3.62 B |
| [Mombasa](Mombasa/README.md) | 1,350,000 | 190 | $1.45 B | $340.4 M | $1.11 B |
| [Nakuru](Nakuru/README.md) | 700,000 | 116 | $423.5 M | $102.3 M | $321.2 M |
| [Kisumu](Kisumu/README.md) | 600,000 | 115 | $431.1 M | $107.7 M | $323.5 M |
| [Eldoret](Eldoret/README.md) | 500,000 | 163 | $481.6 M | $120.5 M | $361.0 M |
| [Thika](Thika/README.md) | 350,000 | 161 | $619.3 M | $152.8 M | $466.6 M |
| [Garissa](Garissa/README.md) | 300,000 | 57 | $216.4 M | $46.1 M | $170.3 M |
| [Kakamega](Kakamega/README.md) | 300,000 | 83 | $312.3 M | $69.5 M | $242.8 M |
| [Kisii](Kisii/README.md) | 300,000 | 52 | $205.1 M | $44.8 M | $160.3 M |
| [Kitale](Kitale/README.md) | 300,000 | 84 | $300.6 M | $67.0 M | $233.6 M |
| [Machakos](Machakos/README.md) | 300,000 | 63 | $235.7 M | $50.5 M | $185.2 M |
| [Malindi](Malindi/README.md) | 300,000 | 61 | $256.1 M | $55.5 M | $200.7 M |
| [Meru Ke](Meru-Ke/README.md) | 250,000 | 61 | $237.3 M | $50.8 M | $186.6 M |
| [Naivasha](Naivasha/README.md) | 250,000 | 79 | $274.4 M | $59.9 M | $214.6 M |
| [Nyeri](Nyeri/README.md) | 250,000 | 76 | $375.8 M | $77.0 M | $298.8 M |

## Local Basis And Regeneration

Country finance parameters use `KE` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 scripts/generate-national-briefs.py
```
