# Syria National OpenSourceRail Strategy

This page contains only Syria-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$32.33 B (88.6%) of external capital** and **$41.77 B of external interest**. Capital plus saved interest totals **$74.10 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 9 |
| Represented population | 7,617,000 |
| Trainsets / vehicle modules | 2,753 / 9,079 |
| City infrastructure and fleet CAPEX | $19.34 B |
| Shared national factory | $863.1 M |
| Factory sizing basis | 2,228 modules for Damascus, then reused nationally |
| **Total national programme** | **$20.27 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $4.14 B (20.5%) |
| Domestic / local capital | $16.12 B (79.5%) |
| Annual external capital draw | $414.5 M / yr |
| Annual local capital draw | $1.61 B / yr |
| Annual public construction commitment | $3.09 B / yr for 10 years |
| Annual post-grace debt service | $2.84 B / yr |
| Default foreign-turnkey external capital | $36.48 B |
| External capital saved | $32.33 B |
| Capital + lifetime external interest saved | $74.10 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $9.26 B | $1.39 B | $7.87 B |
| Stations | $3.89 B | $779.0 M | $3.12 B |
| Depots | $1.75 B | $438.2 M | $1.31 B |
| Rolling stock | $2.63 B | $920.3 M | $1.71 B |
| Dedicated solar plants | $386.8 M | $174.1 M | $212.7 M |
| Residual train control | $50.5 M | $25.3 M | $25.3 M |
| Charging microgrids | $129.1 M | $51.6 M | $77.4 M |
| EPC / project services | $1.30 B | $195.1 M | $1.11 B |
| Shared national trainset factory | $863.1 M | $172.6 M | $690.5 M |
| **Total** | **$20.27 B** | **$4.14 B** | **$16.12 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Damascus](Damascus/README.md) | 2,503,000 | 557 | $4.95 B | $1.02 B | $3.93 B |
| [Aleppo](Aleppo/README.md) | 1,639,000 | 503 | $4.66 B | $963.2 M | $3.70 B |
| [Homs](Homs/README.md) | 775,000 | 234 | $1.35 B | $276.9 M | $1.07 B |
| [Latakia](Latakia/README.md) | 700,000 | 210 | $1.13 B | $233.7 M | $893.0 M |
| [Hama](Hama/README.md) | 600,000 | 297 | $1.59 B | $329.1 M | $1.26 B |
| [Deir Ez Zor](Deir-Ez-Zor/README.md) | 500,000 | 395 | $2.27 B | $465.2 M | $1.80 B |
| [Raqqa](Raqqa/README.md) | 350,000 | 317 | $1.88 B | $382.0 M | $1.49 B |
| [Idlib](Idlib/README.md) | 300,000 | 132 | $780.0 M | $151.7 M | $628.3 M |
| [Tartus](Tartus/README.md) | 250,000 | 108 | $742.5 M | $141.5 M | $601.0 M |

## Local Basis And Regeneration

Country finance parameters use `SY` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

| City | Current lines | Added residential lines | Original station circles | Current station circles |
| --- | ---: | ---: | ---: | ---: |
| [Aleppo](Aleppo/README.md) | 22 | 16 | 44.1% | 78.2% |
| [Damascus](Damascus/README.md) | 25 | 19 | 38.4% | 79.8% |
| [Deir Ez Zor](Deir-Ez-Zor/README.md) | 12 | 9 | 43.1% | 81.4% |
| [Hama](Hama/README.md) | 11 | 8 | 33.5% | 69.2% |
| [Homs](Homs/README.md) | 10 | 7 | 29.8% | 60.3% |
| [Idlib](Idlib/README.md) | 7 | 4 | 55.7% | 81.1% |
| [Latakia](Latakia/README.md) | 10 | 7 | 37.5% | 78.9% |
| [Raqqa](Raqqa/README.md) | 9 | 6 | 42.1% | 75.1% |
| [Tartus](Tartus/README.md) | 7 | 4 | 43.7% | 78.0% |

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
