# Yemen National OpenSourceRail Strategy

This page contains only Yemen-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$23.90 B (88.3%) of external capital** and **$30.87 B of external interest**. Capital plus saved interest totals **$54.77 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 9 |
| Represented population | 8,337,500 |
| Trainsets / vehicle modules | 2,177 / 7,896 |
| City infrastructure and fleet CAPEX | $14.13 B |
| Shared national factory | $853.9 M |
| Factory sizing basis | 3,396 modules for Sanaa, then reused nationally |
| **Total national programme** | **$15.04 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $3.17 B (21.1%) |
| Domestic / local capital | $11.87 B (78.9%) |
| Annual external capital draw | $317.4 M / yr |
| Annual local capital draw | $1.19 B / yr |
| Annual public construction commitment | $2.09 B / yr for 10 years |
| Annual post-grace debt service | $1.92 B / yr |
| Default foreign-turnkey external capital | $27.07 B |
| External capital saved | $23.90 B |
| Capital + lifetime external interest saved | $54.77 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $6.30 B | $944.9 M | $5.35 B |
| Stations | $2.84 B | $567.2 M | $2.27 B |
| Depots | $1.31 B | $328.2 M | $984.7 M |
| Rolling stock | $2.29 B | $800.6 M | $1.49 B |
| Dedicated solar plants | $359.9 M | $162.0 M | $198.0 M |
| Residual train control | $36.1 M | $18.0 M | $18.0 M |
| Charging microgrids | $94.1 M | $37.6 M | $56.4 M |
| EPC / project services | $960.4 M | $144.1 M | $816.3 M |
| Shared national trainset factory | $853.9 M | $170.8 M | $683.1 M |
| **Total** | **$15.04 B** | **$3.17 B** | **$11.87 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Sanaa](Sanaa/README.md) | 3,937,500 | 566 | $5.18 B | $1.16 B | $4.02 B |
| [Aden](Aden/README.md) | 985,000 | 253 | $1.38 B | $286.5 M | $1.09 B |
| [Hodeidah](Hodeidah/README.md) | 750,000 | 176 | $946.0 M | $196.6 M | $749.5 M |
| [Ibb](Ibb/README.md) | 750,000 | 279 | $1.48 B | $307.1 M | $1.17 B |
| [Taiz](Taiz/README.md) | 615,000 | 269 | $1.40 B | $293.5 M | $1.11 B |
| [Mukalla](Mukalla/README.md) | 550,000 | 301 | $1.59 B | $336.5 M | $1.25 B |
| [Dhamar](Dhamar/README.md) | 300,000 | 110 | $676.1 M | $132.6 M | $543.6 M |
| [Lahij](Lahij/README.md) | 250,000 | 123 | $777.9 M | $149.2 M | $628.7 M |
| [Sayun](Sayun/README.md) | 200,000 | 100 | $697.7 M | $134.4 M | $563.3 M |

## Local Basis And Regeneration

Country finance parameters use `YE` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

| City | Current lines | Added residential lines | Original station circles | Current station circles |
| --- | ---: | ---: | ---: | ---: |
| [Aden](Aden/README.md) | 9 | 6 | 45.6% | 79.3% |
| [Dhamar](Dhamar/README.md) | 8 | 5 | 34.5% | 71.1% |
| [Hodeidah](Hodeidah/README.md) | 9 | 6 | 39.3% | 68.8% |
| [Ibb](Ibb/README.md) | 11 | 8 | 21.0% | 47.4% |
| [Lahij](Lahij/README.md) | 7 | 4 | 54.9% | 80.3% |
| [Mukalla](Mukalla/README.md) | 7 | 4 | 49.7% | 81.9% |
| [Sanaa](Sanaa/README.md) | 13 | 6 | 61.4% | 81.9% |
| [Sayun](Sayun/README.md) | 6 | 3 | 57.4% | 83.2% |
| [Taiz](Taiz/README.md) | 11 | 8 | 36.3% | 75.3% |

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
