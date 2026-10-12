# Kenya National OpenSourceRail Strategy

This page contains only Kenya-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$44.42 B (88.3%) of external capital** and **$55.69 B of external interest**. Capital plus saved interest totals **$100.11 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 15 |
| Represented population | 11,750,000 |
| Trainsets / vehicle modules | 3,181 / 12,630 |
| City infrastructure and fleet CAPEX | $27.14 B |
| Shared national factory | $750.0 M |
| Factory sizing basis | 6,768 modules for Nairobi, then reused nationally |
| **Total national programme** | **$27.95 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $5.88 B (21.1%) |
| Domestic / local capital | $22.06 B (78.9%) |
| Annual external capital draw | $840.5 M / yr |
| Annual local capital draw | $3.15 B / yr |
| Annual public construction commitment | $2.92 B / yr for 7 years |
| Annual post-grace debt service | $2.43 B / yr |
| Default foreign-turnkey external capital | $50.31 B |
| External capital saved | $44.42 B |
| Capital + lifetime external interest saved | $100.11 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $13.81 B | $2.07 B | $11.74 B |
| Stations | $4.71 B | $942.1 M | $3.77 B |
| Depots | $1.51 B | $377.2 M | $1.13 B |
| Rolling stock | $3.59 B | $1.26 B | $2.33 B |
| Dedicated solar plants | $1.58 B | $711.3 M | $869.4 M |
| Residual train control | $73.9 M | $37.0 M | $37.0 M |
| Charging microgrids | $198.1 M | $79.2 M | $118.9 M |
| EPC / project services | $1.72 B | $258.7 M | $1.47 B |
| Shared national trainset factory | $750.0 M | $150.0 M | $600.0 M |
| **Total** | **$27.95 B** | **$5.88 B** | **$22.06 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital | Lines | Added lines | Original circles | Current circles |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| [Nairobi](Nairobi/README.md) | 5,700,000 | 1,128 | $11.72 B | $2.65 B | $9.07 B | 14 | 5 | 39.3% | 38.4% |
| [Mombasa](Mombasa/README.md) | 1,350,000 | 423 | $5.18 B | $1.05 B | $4.13 B | 9 | 3 | 49.5% | 48.0% |
| [Nakuru](Nakuru/README.md) | 700,000 | 202 | $1.09 B | $225.1 M | $865.8 M | 5 | 2 | 28.0% | 48.0% |
| [Kisumu](Kisumu/README.md) | 600,000 | 191 | $1.08 B | $224.0 M | $851.2 M | 5 | 2 | 26.2% | 32.4% |
| [Eldoret](Eldoret/README.md) | 500,000 | 261 | $1.45 B | $302.6 M | $1.15 B | 5 | 2 | 33.1% | 44.0% |
| [Thika](Thika/README.md) | 350,000 | 256 | $1.34 B | $284.9 M | $1.05 B | 5 | 2 | 28.8% | 29.0% |
| [Garissa](Garissa/README.md) | 300,000 | 57 | $394.6 M | $74.9 M | $319.7 M | 4 | 1 | 55.0% | 61.8% |
| [Kakamega](Kakamega/README.md) | 300,000 | 98 | $754.4 M | $141.2 M | $613.1 M | 4 | 1 | 31.8% | 35.7% |
| [Kisii](Kisii/README.md) | 300,000 | 69 | $512.2 M | $95.9 M | $416.3 M | 4 | 1 | 21.4% | 26.4% |
| [Kitale](Kitale/README.md) | 300,000 | 99 | $727.1 M | $137.5 M | $589.6 M | 4 | 1 | 15.9% | 37.1% |
| [Machakos](Machakos/README.md) | 300,000 | 68 | $480.0 M | $89.2 M | $390.8 M | 4 | 1 | 28.4% | 34.7% |
| [Malindi](Malindi/README.md) | 300,000 | 68 | $497.2 M | $92.9 M | $404.4 M | 4 | 1 | 41.1% | 48.8% |
| [Meru Ke](Meru-Ke/README.md) | 250,000 | 65 | $473.8 M | $87.8 M | $386.0 M | 4 | 1 | 25.7% | 30.3% |
| [Naivasha](Naivasha/README.md) | 250,000 | 110 | $796.6 M | $150.5 M | $646.1 M | 4 | 1 | 49.3% | 45.5% |
| [Nyeri](Nyeri/README.md) | 250,000 | 86 | $656.4 M | $122.4 M | $534.0 M | 4 | 1 | 29.0% | 30.5% |

## Local Basis And Regeneration

Country finance parameters use `KE` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
