# Kenya National OpenSourceRail Strategy

This page contains only Kenya-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$63.82 B (88.1%) of external capital** and **$80.01 B of external interest**. Capital plus saved interest totals **$143.83 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 15 |
| Represented population | 11,750,000 |
| Trainsets / vehicle modules | 5,304 / 20,543 |
| City infrastructure and fleet CAPEX | $39.31 B |
| Shared national factory | $868.2 M |
| Factory sizing basis | 10,524 modules for Nairobi, then reused nationally |
| **Total national programme** | **$40.24 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $8.61 B (21.4%) |
| Domestic / local capital | $31.63 B (78.6%) |
| Annual external capital draw | $1.23 B / yr |
| Annual local capital draw | $4.52 B / yr |
| Annual public construction commitment | $4.20 B / yr for 7 years |
| Annual post-grace debt service | $3.50 B / yr |
| Default foreign-turnkey external capital | $72.43 B |
| External capital saved | $63.82 B |
| Capital + lifetime external interest saved | $143.83 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $17.67 B | $2.65 B | $15.02 B |
| Stations | $7.92 B | $1.58 B | $6.34 B |
| Depots | $3.25 B | $811.4 M | $2.43 B |
| Rolling stock | $5.84 B | $2.05 B | $3.80 B |
| Dedicated solar plants | $1.73 B | $779.8 M | $953.1 M |
| Residual train control | $100.5 M | $50.3 M | $50.3 M |
| Charging microgrids | $334.7 M | $133.9 M | $200.8 M |
| EPC / project services | $2.52 B | $377.9 M | $2.14 B |
| Shared national trainset factory | $868.2 M | $173.6 M | $694.6 M |
| **Total** | **$40.24 B** | **$8.61 B** | **$31.63 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Nairobi](Nairobi/README.md) | 5,700,000 | 1,754 | $15.45 B | $3.59 B | $11.86 B |
| [Mombasa](Mombasa/README.md) | 1,350,000 | 690 | $6.79 B | $1.42 B | $5.38 B |
| [Nakuru](Nakuru/README.md) | 700,000 | 343 | $1.77 B | $369.2 M | $1.40 B |
| [Kisumu](Kisumu/README.md) | 600,000 | 306 | $1.75 B | $363.7 M | $1.39 B |
| [Eldoret](Eldoret/README.md) | 500,000 | 400 | $2.15 B | $443.3 M | $1.70 B |
| [Thika](Thika/README.md) | 350,000 | 490 | $2.43 B | $524.6 M | $1.90 B |
| [Garissa](Garissa/README.md) | 300,000 | 84 | $561.8 M | $108.1 M | $453.7 M |
| [Kakamega](Kakamega/README.md) | 300,000 | 201 | $1.27 B | $245.5 M | $1.02 B |
| [Kisii](Kisii/README.md) | 300,000 | 96 | $624.7 M | $121.2 M | $503.6 M |
| [Kitale](Kitale/README.md) | 300,000 | 195 | $1.31 B | $251.5 M | $1.05 B |
| [Machakos](Machakos/README.md) | 300,000 | 123 | $820.0 M | $158.3 M | $661.8 M |
| [Malindi](Malindi/README.md) | 300,000 | 123 | $857.5 M | $163.8 M | $693.6 M |
| [Meru Ke](Meru-Ke/README.md) | 250,000 | 124 | $988.7 M | $183.5 M | $805.3 M |
| [Naivasha](Naivasha/README.md) | 250,000 | 191 | $1.25 B | $241.1 M | $1.01 B |
| [Nyeri](Nyeri/README.md) | 250,000 | 184 | $1.29 B | $244.8 M | $1.05 B |

## Local Basis And Regeneration

Country finance parameters use `KE` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

| City | Current lines | Added residential lines | Original station circles | Current station circles |
| --- | ---: | ---: | ---: | ---: |
| [Eldoret](Eldoret/README.md) | 16 | 13 | 33.1% | 75.9% |
| [Garissa](Garissa/README.md) | 6 | 3 | 55.0% | 80.7% |
| [Kakamega](Kakamega/README.md) | 11 | 8 | 31.8% | 59.3% |
| [Kisii](Kisii/README.md) | 7 | 4 | 21.4% | 41.1% |
| [Kisumu](Kisumu/README.md) | 12 | 9 | 26.2% | 70.9% |
| [Kitale](Kitale/README.md) | 13 | 10 | 15.9% | 68.9% |
| [Machakos](Machakos/README.md) | 8 | 5 | 28.4% | 56.7% |
| [Malindi](Malindi/README.md) | 8 | 5 | 41.1% | 70.1% |
| [Meru Ke](Meru-Ke/README.md) | 9 | 6 | 25.7% | 54.9% |
| [Mombasa](Mombasa/README.md) | 17 | 11 | 49.5% | 83.5% |
| [Nairobi](Nairobi/README.md) | 41 | 32 | 39.3% | 80.3% |
| [Naivasha](Naivasha/README.md) | 10 | 7 | 49.3% | 78.1% |
| [Nakuru](Nakuru/README.md) | 13 | 10 | 28.0% | 75.4% |
| [Nyeri](Nyeri/README.md) | 10 | 7 | 29.0% | 66.1% |
| [Thika](Thika/README.md) | 15 | 12 | 28.8% | 65.7% |

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
