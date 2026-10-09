# Cambodia National OpenSourceRail Strategy

This page contains only Cambodia-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$13.28 B (88.6%) of external capital** and **$16.65 B of external interest**. Capital plus saved interest totals **$29.93 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 2,281,000 |
| Trainsets / vehicle modules | 828 / 3,312 |
| City infrastructure and fleet CAPEX | $8.08 B |
| Shared national factory | $232.2 M |
| Factory sizing basis | 3,312 modules for Phnom Penh, then reused nationally |
| **Total national programme** | **$8.33 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.71 B (20.5%) |
| Domestic / local capital | $6.62 B (79.5%) |
| Annual external capital draw | $243.6 M / yr |
| Annual local capital draw | $945.7 M / yr |
| Annual public construction commitment | $689.6 M / yr for 7 years |
| Annual post-grace debt service | $560.1 M / yr |
| Default foreign-turnkey external capital | $14.99 B |
| External capital saved | $13.28 B |
| Capital + lifetime external interest saved | $29.93 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $4.14 B | $620.9 M | $3.52 B |
| Stations | $1.60 B | $319.9 M | $1.28 B |
| Depots | $448.3 M | $112.1 M | $336.2 M |
| Rolling stock | $927.4 M | $324.6 M | $602.8 M |
| Dedicated solar plants | $366.2 M | $164.8 M | $201.4 M |
| Residual train control | $19.2 M | $9.6 M | $9.6 M |
| Charging microgrids | $73.0 M | $29.2 M | $43.8 M |
| EPC / project services | $520.7 M | $78.1 M | $442.6 M |
| Shared national trainset factory | $232.2 M | $46.4 M | $185.7 M |
| **Total** | **$8.33 B** | **$1.71 B** | **$6.62 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Phnom Penh](Phnom-Penh/README.md) | 2,281,000 | 828 | $8.08 B | $1.66 B | $6.42 B |

## Local Basis And Regeneration

Country finance parameters use `KH` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

| City | Current lines | Added residential lines | Original station circles | Current station circles |
| --- | ---: | ---: | ---: | ---: |
| [Phnom Penh](Phnom-Penh/README.md) | 25 | 19 | 34.2% | 80.3% |

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
