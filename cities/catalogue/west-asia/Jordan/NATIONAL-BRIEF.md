# Jordan National OpenSourceRail Strategy

This page contains only Jordan-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$25.65 B (88.0%) of external capital** and **$31.54 B of external interest**. Capital plus saved interest totals **$57.19 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 4 |
| Represented population | 5,557,000 |
| Trainsets / vehicle modules | 1,952 / 9,286 |
| City infrastructure and fleet CAPEX | $15.28 B |
| Shared national factory | $863.1 M |
| Factory sizing basis | 7,068 modules for Amman, then reused nationally |
| **Total national programme** | **$16.20 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $3.51 B (21.7%) |
| Domestic / local capital | $12.69 B (78.3%) |
| Annual external capital draw | $702.5 M / yr |
| Annual local capital draw | $2.54 B / yr |
| Annual public construction commitment | $1.43 B / yr for 5 years |
| Annual post-grace debt service | $1.03 B / yr |
| Default foreign-turnkey external capital | $29.17 B |
| External capital saved | $25.65 B |
| Capital + lifetime external interest saved | $57.19 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $6.82 B | $1.02 B | $5.80 B |
| Stations | $2.87 B | $574.7 M | $2.30 B |
| Depots | $1.13 B | $281.9 M | $845.7 M |
| Rolling stock | $2.64 B | $924.1 M | $1.72 B |
| Dedicated solar plants | $688.7 M | $309.9 M | $378.8 M |
| Residual train control | $36.9 M | $18.5 M | $18.5 M |
| Charging microgrids | $139.2 M | $55.7 M | $83.5 M |
| EPC / project services | $1.01 B | $152.2 M | $862.7 M |
| Shared national trainset factory | $863.1 M | $172.6 M | $690.5 M |
| **Total** | **$16.20 B** | **$3.51 B** | **$12.69 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Amman](Amman/README.md) | 4,007,000 | 1,178 | $10.73 B | $2.41 B | $8.33 B |
| [Zarqa](Zarqa/README.md) | 700,000 | 391 | $2.40 B | $485.8 M | $1.92 B |
| [Irbid](Irbid/README.md) | 600,000 | 279 | $1.46 B | $306.0 M | $1.15 B |
| [Aqaba](Aqaba/README.md) | 250,000 | 104 | $686.2 M | $130.6 M | $555.6 M |

## Local Basis And Regeneration

Country finance parameters use `JO` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

| City | Current lines | Added residential lines | Original station circles | Current station circles |
| --- | ---: | ---: | ---: | ---: |
| [Amman](Amman/README.md) | 31 | 22 | 46.2% | 82.4% |
| [Aqaba](Aqaba/README.md) | 5 | 2 | 58.2% | 79.5% |
| [Irbid](Irbid/README.md) | 12 | 9 | 27.7% | 60.1% |
| [Zarqa](Zarqa/README.md) | 13 | 10 | 33.6% | 77.3% |

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
