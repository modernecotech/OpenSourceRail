# Guinea National OpenSourceRail Strategy

This page contains only Guinea-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$5.53 B (88.6%) of external capital** and **$7.15 B of external interest**. Capital plus saved interest totals **$12.68 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 2,010,000 |
| Trainsets / vehicle modules | 286 / 1,144 |
| City infrastructure and fleet CAPEX | $2.57 B |
| Shared national factory | $841.3 M |
| Factory sizing basis | 1,144 modules for Conakry, then reused nationally |
| **Total national programme** | **$3.47 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $714.6 M (20.6%) |
| Domestic / local capital | $2.76 B (79.4%) |
| Annual external capital draw | $71.5 M / yr |
| Annual local capital draw | $275.7 M / yr |
| Annual public construction commitment | $307.9 M / yr for 10 years |
| Annual post-grace debt service | $277.9 M / yr |
| Default foreign-turnkey external capital | $6.25 B |
| External capital saved | $5.53 B |
| Capital + lifetime external interest saved | $12.68 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $1.18 B | $176.4 M | $999.7 M |
| Stations | $565.2 M | $113.0 M | $452.2 M |
| Depots | $219.3 M | $54.8 M | $164.5 M |
| Rolling stock | $320.3 M | $112.1 M | $208.2 M |
| Dedicated solar plants | $92.8 M | $41.8 M | $51.1 M |
| Residual train control | $6.7 M | $3.4 M | $3.4 M |
| Charging microgrids | $29.0 M | $11.6 M | $17.4 M |
| EPC / project services | $221.1 M | $33.2 M | $187.9 M |
| Shared national trainset factory | $841.3 M | $168.3 M | $673.0 M |
| **Total** | **$3.47 B** | **$714.6 M** | **$2.76 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Conakry](Conakry/README.md) | 2,010,000 | 286 | $2.57 B | $537.5 M | $2.03 B |

## Local Basis And Regeneration

Country finance parameters use `GN` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

| City | Current lines | Added residential lines | Original station circles | Current station circles |
| --- | ---: | ---: | ---: | ---: |
| [Conakry](Conakry/README.md) | 14 | 11 | 26.0% | 80.0% |

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
