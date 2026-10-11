# Pakistan National OpenSourceRail Strategy

This page contains only Pakistan-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$87.29 B (88.3%) of external capital** and **$109.42 B of external interest**. Capital plus saved interest totals **$196.71 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 13 |
| Represented population | 37,603,000 |
| Trainsets / vehicle modules | 6,538 / 28,799 |
| City infrastructure and fleet CAPEX | $53.99 B |
| Shared national factory | $863.1 M |
| Factory sizing basis | 9,186 modules for Karachi, then reused nationally |
| **Total national programme** | **$54.91 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $11.55 B (21.0%) |
| Domestic / local capital | $43.36 B (79.0%) |
| Annual external capital draw | $1.65 B / yr |
| Annual local capital draw | $6.19 B / yr |
| Annual public construction commitment | $7.48 B / yr for 7 years |
| Annual post-grace debt service | $6.44 B / yr |
| Default foreign-turnkey external capital | $98.84 B |
| External capital saved | $87.29 B |
| Capital + lifetime external interest saved | $196.71 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $25.33 B | $3.80 B | $21.53 B |
| Stations | $10.52 B | $2.10 B | $8.41 B |
| Depots | $4.17 B | $1.04 B | $3.13 B |
| Rolling stock | $8.17 B | $2.86 B | $5.31 B |
| Dedicated solar plants | $1.73 B | $780.0 M | $953.3 M |
| Residual train control | $133.2 M | $66.6 M | $66.6 M |
| Charging microgrids | $520.8 M | $208.3 M | $312.5 M |
| EPC / project services | $3.48 B | $521.8 M | $2.96 B |
| Shared national trainset factory | $863.1 M | $172.6 M | $690.5 M |
| **Total** | **$54.91 B** | **$11.55 B** | **$43.36 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Karachi](Karachi/README.md) | 20,300,000 | 1,531 | $14.34 B | $3.18 B | $11.16 B |
| [Faisalabad](Faisalabad/README.md) | 3,556,000 | 650 | $5.63 B | $1.26 B | $4.37 B |
| [Gujranwala](Gujranwala/README.md) | 2,300,000 | 777 | $6.57 B | $1.37 B | $5.20 B |
| [Peshawar](Peshawar/README.md) | 2,300,000 | 688 | $6.21 B | $1.27 B | $4.94 B |
| [Multan](Multan/README.md) | 2,197,000 | 432 | $3.72 B | $763.8 M | $2.96 B |
| [Hyderabad Pk](Hyderabad-Pk/README.md) | 1,900,000 | 378 | $3.71 B | $746.2 M | $2.96 B |
| [Quetta](Quetta/README.md) | 1,200,000 | 367 | $3.32 B | $673.7 M | $2.65 B |
| [Bahawalpur](Bahawalpur/README.md) | 900,000 | 267 | $1.36 B | $285.0 M | $1.08 B |
| [Sialkot](Sialkot/README.md) | 750,000 | 397 | $2.59 B | $507.6 M | $2.08 B |
| [Sheikhupura](Sheikhupura/README.md) | 600,000 | 173 | $891.4 M | $190.5 M | $700.9 M |
| [Sukkur](Sukkur/README.md) | 600,000 | 277 | $2.03 B | $390.6 M | $1.64 B |
| [Larkana](Larkana/README.md) | 500,000 | 238 | $1.70 B | $327.9 M | $1.37 B |
| [Rahim Yar Khan](Rahim-Yar-Khan/README.md) | 500,000 | 363 | $1.92 B | $403.4 M | $1.52 B |

## Local Basis And Regeneration

Country finance parameters use `PK` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

| City | Current lines | Added residential lines | Original station circles | Current station circles |
| --- | ---: | ---: | ---: | ---: |
| [Bahawalpur](Bahawalpur/README.md) | 10 | 7 | 35.6% | 74.0% |
| [Faisalabad](Faisalabad/README.md) | 23 | 17 | 40.9% | 80.2% |
| [Gujranwala](Gujranwala/README.md) | 33 | 28 | 29.1% | 80.0% |
| [Hyderabad Pk](Hyderabad-Pk/README.md) | 15 | 9 | 49.4% | 82.8% |
| [Karachi](Karachi/README.md) | 33 | 24 | 47.7% | 83.7% |
| [Larkana](Larkana/README.md) | 9 | 7 | 22.2% | 79.1% |
| [Multan](Multan/README.md) | 25 | 20 | 34.3% | 78.1% |
| [Peshawar](Peshawar/README.md) | 31 | 26 | 24.3% | 69.2% |
| [Quetta](Quetta/README.md) | 22 | 18 | 32.0% | 72.0% |
| [Rahim Yar Khan](Rahim-Yar-Khan/README.md) | 10 | 7 | 20.7% | 67.4% |
| [Sheikhupura](Sheikhupura/README.md) | 5 | 3 | 14.9% | 34.8% |
| [Sialkot](Sialkot/README.md) | 17 | 14 | 28.1% | 65.9% |
| [Sukkur](Sukkur/README.md) | 12 | 9 | 28.9% | 76.0% |

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
