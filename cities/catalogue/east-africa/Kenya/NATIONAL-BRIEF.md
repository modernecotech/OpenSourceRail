# Kenya National OpenSourceRail Strategy

This page contains only Kenya-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$27.37 B (88.3%) of external capital** and **$34.31 B of external interest**. Capital plus saved interest totals **$61.68 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 15 |
| Represented population | 11,750,000 |
| Trainsets / vehicle modules | 2,044 / 7,867 |
| City infrastructure and fleet CAPEX | $16.56 B |
| Shared national factory | $615.0 M |
| Factory sizing basis | 4,188 modules for Nairobi, then reused nationally |
| **Total national programme** | **$17.22 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $3.63 B (21.1%) |
| Domestic / local capital | $13.59 B (78.9%) |
| Annual external capital draw | $517.9 M / yr |
| Annual local capital draw | $1.94 B / yr |
| Annual public construction commitment | $1.80 B / yr for 7 years |
| Annual post-grace debt service | $1.50 B / yr |
| Default foreign-turnkey external capital | $31.00 B |
| External capital saved | $27.37 B |
| Capital + lifetime external interest saved | $61.68 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $9.56 B | $1.43 B | $8.13 B |
| Stations | $1.44 B | $288.7 M | $1.15 B |
| Depots | $1.00 B | $250.2 M | $750.6 M |
| Rolling stock | $2.24 B | $784.5 M | $1.46 B |
| Dedicated solar plants | $1.17 B | $528.6 M | $646.0 M |
| Residual train control | $52.4 M | $26.2 M | $26.2 M |
| Charging microgrids | $81.6 M | $32.6 M | $49.0 M |
| EPC / project services | $1.05 B | $157.5 M | $892.2 M |
| Shared national trainset factory | $615.0 M | $123.0 M | $492.0 M |
| **Total** | **$17.22 B** | **$3.63 B** | **$13.59 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Nairobi](Nairobi/README.md) | 5,700,000 | 698 | $7.15 B | $1.64 B | $5.52 B |
| [Mombasa](Mombasa/README.md) | 1,350,000 | 171 | $2.17 B | $433.3 M | $1.74 B |
| [Nakuru](Nakuru/README.md) | 700,000 | 144 | $983.5 M | $190.5 M | $793.0 M |
| [Kisumu](Kisumu/README.md) | 600,000 | 127 | $678.8 M | $142.9 M | $535.9 M |
| [Eldoret](Eldoret/README.md) | 500,000 | 167 | $828.0 M | $174.3 M | $653.7 M |
| [Thika](Thika/README.md) | 350,000 | 207 | $994.9 M | $216.1 M | $778.8 M |
| [Garissa](Garissa/README.md) | 300,000 | 41 | $277.0 M | $52.3 M | $224.8 M |
| [Kakamega](Kakamega/README.md) | 300,000 | 78 | $515.7 M | $97.8 M | $417.9 M |
| [Kisii](Kisii/README.md) | 300,000 | 42 | $278.6 M | $52.8 M | $225.8 M |
| [Kitale](Kitale/README.md) | 300,000 | 74 | $498.0 M | $94.7 M | $403.3 M |
| [Machakos](Machakos/README.md) | 300,000 | 50 | $343.1 M | $64.2 M | $278.8 M |
| [Malindi](Malindi/README.md) | 300,000 | 51 | $358.1 M | $67.1 M | $291.0 M |
| [Meru Ke](Meru-Ke/README.md) | 250,000 | 51 | $407.0 M | $74.1 M | $332.8 M |
| [Naivasha](Naivasha/README.md) | 250,000 | 74 | $484.7 M | $90.3 M | $394.4 M |
| [Nyeri](Nyeri/README.md) | 250,000 | 69 | $592.4 M | $107.7 M | $484.7 M |

## Local Basis And Regeneration

Country finance parameters use `KE` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
