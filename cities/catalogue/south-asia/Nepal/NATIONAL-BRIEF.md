# Nepal National OpenSourceRail Strategy

This page contains only Nepal-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$12.08 B (88.7%) of external capital** and **$15.14 B of external interest**. Capital plus saved interest totals **$27.23 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 3 |
| Represented population | 2,342,000 |
| Trainsets / vehicle modules | 850 / 2,817 |
| City infrastructure and fleet CAPEX | $6.65 B |
| Shared national factory | $863.1 M |
| Factory sizing basis | 1,544 modules for Kathmandu, then reused nationally |
| **Total national programme** | **$7.57 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.55 B (20.4%) |
| Domestic / local capital | $6.02 B (79.6%) |
| Annual external capital draw | $220.8 M / yr |
| Annual local capital draw | $860.7 M / yr |
| Annual public construction commitment | $603.2 M / yr for 7 years |
| Annual post-grace debt service | $488.9 M / yr |
| Default foreign-turnkey external capital | $13.63 B |
| External capital saved | $12.08 B |
| Capital + lifetime external interest saved | $27.23 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $3.41 B | $511.8 M | $2.90 B |
| Stations | $1.21 B | $242.8 M | $971.0 M |
| Depots | $462.8 M | $115.7 M | $347.1 M |
| Rolling stock | $809.5 M | $283.3 M | $526.1 M |
| Dedicated solar plants | $269.3 M | $121.2 M | $148.1 M |
| Residual train control | $17.9 M | $8.9 M | $8.9 M |
| Charging microgrids | $44.5 M | $17.8 M | $26.7 M |
| EPC / project services | $477.6 M | $71.6 M | $406.0 M |
| Shared national trainset factory | $863.1 M | $172.6 M | $690.5 M |
| **Total** | **$7.57 B** | **$1.55 B** | **$6.02 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Kathmandu](Kathmandu/README.md) | 1,442,000 | 386 | $3.69 B | $779.9 M | $2.91 B |
| [Pokhara](Pokhara/README.md) | 600,000 | 345 | $1.99 B | $408.5 M | $1.58 B |
| [Biratnagar](Biratnagar/README.md) | 300,000 | 119 | $965.4 M | $175.8 M | $789.6 M |

## Local Basis And Regeneration

Country finance parameters use `NP` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

| City | Current lines | Added residential lines | Original station circles | Current station circles |
| --- | ---: | ---: | ---: | ---: |
| [Biratnagar](Biratnagar/README.md) | 6 | 3 | 26.2% | 69.3% |
| [Kathmandu](Kathmandu/README.md) | 13 | 7 | 53.0% | 80.8% |
| [Pokhara](Pokhara/README.md) | 9 | 6 | 43.2% | 84.5% |

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
