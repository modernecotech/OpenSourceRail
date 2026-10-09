# Bolivia National OpenSourceRail Strategy

This page contains only Bolivia-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$10.52 B (88.5%) of external capital** and **$12.93 B of external interest**. Capital plus saved interest totals **$23.44 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 1,815,000 |
| Trainsets / vehicle modules | 667 / 2,668 |
| City infrastructure and fleet CAPEX | $6.32 B |
| Shared national factory | $255.8 M |
| Factory sizing basis | 2,668 modules for La Paz, then reused nationally |
| **Total national programme** | **$6.60 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.36 B (20.6%) |
| Domestic / local capital | $5.24 B (79.4%) |
| Annual external capital draw | $272.0 M / yr |
| Annual local capital draw | $1.05 B / yr |
| Annual public construction commitment | $710.7 M / yr for 5 years |
| Annual post-grace debt service | $531.6 M / yr |
| Default foreign-turnkey external capital | $11.88 B |
| External capital saved | $10.52 B |
| Capital + lifetime external interest saved | $23.44 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $3.07 B | $460.0 M | $2.61 B |
| Stations | $1.37 B | $273.6 M | $1.09 B |
| Depots | $408.0 M | $102.0 M | $306.0 M |
| Rolling stock | $747.0 M | $261.5 M | $485.6 M |
| Dedicated solar plants | $259.6 M | $116.8 M | $142.8 M |
| Residual train control | $15.5 M | $7.8 M | $7.8 M |
| Charging microgrids | $61.8 M | $24.7 M | $37.1 M |
| EPC / project services | $414.6 M | $62.2 M | $352.4 M |
| Shared national trainset factory | $255.8 M | $51.2 M | $204.7 M |
| **Total** | **$6.60 B** | **$1.36 B** | **$5.24 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [La Paz](La-Paz/README.md) | 1,815,000 | 667 | $6.32 B | $1.31 B | $5.02 B |

## Local Basis And Regeneration

Country finance parameters use `BO` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

| City | Current lines | Added residential lines | Original station circles | Current station circles |
| --- | ---: | ---: | ---: | ---: |
| [La Paz](La-Paz/README.md) | 24 | 18 | 39.0% | 81.7% |

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
