# Bangladesh National OpenSourceRail Strategy

This page contains only Bangladesh-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$66.22 B (88.1%) of external capital** and **$83.01 B of external interest**. Capital plus saved interest totals **$149.23 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 10 |
| Represented population | 13,550,000 |
| Trainsets / vehicle modules | 5,336 / 21,957 |
| City infrastructure and fleet CAPEX | $40.84 B |
| Shared national factory | $874.1 M |
| Factory sizing basis | 8,592 modules for Chittagong, then reused nationally |
| **Total national programme** | **$41.78 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $8.98 B (21.5%) |
| Domestic / local capital | $32.80 B (78.5%) |
| Annual external capital draw | $1.28 B / yr |
| Annual local capital draw | $4.69 B / yr |
| Annual public construction commitment | $3.57 B / yr for 7 years |
| Annual post-grace debt service | $2.92 B / yr |
| Default foreign-turnkey external capital | $75.20 B |
| External capital saved | $66.22 B |
| Capital + lifetime external interest saved | $149.23 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $18.64 B | $2.80 B | $15.84 B |
| Stations | $7.93 B | $1.59 B | $6.34 B |
| Depots | $3.04 B | $759.6 M | $2.28 B |
| Rolling stock | $6.28 B | $2.20 B | $4.08 B |
| Dedicated solar plants | $1.97 B | $888.6 M | $1.09 B |
| Residual train control | $98.6 M | $49.3 M | $49.3 M |
| Charging microgrids | $341.6 M | $136.7 M | $205.0 M |
| EPC / project services | $2.60 B | $390.6 M | $2.21 B |
| Shared national trainset factory | $874.1 M | $174.8 M | $699.3 M |
| **Total** | **$41.78 B** | **$8.98 B** | **$32.80 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Chittagong](Chittagong/README.md) | 5,200,000 | 1,432 | $12.92 B | $2.97 B | $9.95 B |
| [Khulna](Khulna/README.md) | 1,500,000 | 531 | $5.46 B | $1.11 B | $4.35 B |
| [Gazipur](Gazipur/README.md) | 1,400,000 | 1,122 | $9.86 B | $2.08 B | $7.77 B |
| [Narayanganj](Narayanganj/README.md) | 950,000 | 533 | $3.10 B | $643.3 M | $2.46 B |
| [Rajshahi](Rajshahi/README.md) | 950,000 | 234 | $1.29 B | $270.9 M | $1.02 B |
| [Sylhet](Sylhet/README.md) | 900,000 | 297 | $1.56 B | $329.5 M | $1.23 B |
| [Rangpur](Rangpur/README.md) | 800,000 | 261 | $1.44 B | $302.3 M | $1.14 B |
| [Mymensingh](Mymensingh/README.md) | 700,000 | 269 | $1.63 B | $331.1 M | $1.30 B |
| [Comilla](Comilla/README.md) | 600,000 | 310 | $1.61 B | $342.7 M | $1.27 B |
| [Barisal](Barisal/README.md) | 550,000 | 347 | $1.97 B | $410.7 M | $1.56 B |

## Local Basis And Regeneration

Country finance parameters use `BD` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

| City | Current lines | Added residential lines | Original station circles | Current station circles |
| --- | ---: | ---: | ---: | ---: |
| [Barisal](Barisal/README.md) | 10 | 7 | 39.6% | 81.8% |
| [Chittagong](Chittagong/README.md) | 37 | 29 | 46.6% | 83.8% |
| [Comilla](Comilla/README.md) | 9 | 6 | 28.7% | 61.0% |
| [Gazipur](Gazipur/README.md) | 41 | 35 | 29.1% | 76.5% |
| [Khulna](Khulna/README.md) | 16 | 10 | 51.8% | 79.3% |
| [Mymensingh](Mymensingh/README.md) | 10 | 7 | 18.8% | 47.8% |
| [Narayanganj](Narayanganj/README.md) | 19 | 16 | 34.2% | 77.6% |
| [Rajshahi](Rajshahi/README.md) | 9 | 6 | 36.1% | 63.8% |
| [Rangpur](Rangpur/README.md) | 11 | 8 | 22.4% | 52.8% |
| [Sylhet](Sylhet/README.md) | 12 | 9 | 25.1% | 56.4% |

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
