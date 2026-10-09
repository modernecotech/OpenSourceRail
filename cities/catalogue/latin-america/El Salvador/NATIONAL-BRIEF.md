# El Salvador National OpenSourceRail Strategy

This page contains only El Salvador-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$10.05 B (88.3%) of external capital** and **$12.36 B of external interest**. Capital plus saved interest totals **$22.41 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 1,800,000 |
| Trainsets / vehicle modules | 659 / 2,636 |
| City infrastructure and fleet CAPEX | $6.05 B |
| Shared national factory | $255.8 M |
| Factory sizing basis | 2,636 modules for San Salvador, then reused nationally |
| **Total national programme** | **$6.32 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.33 B (21.0%) |
| Domestic / local capital | $4.99 B (79.0%) |
| Annual external capital draw | $265.9 M / yr |
| Annual local capital draw | $998.6 M / yr |
| Annual public construction commitment | $718.9 M / yr for 5 years |
| Annual post-grace debt service | $545.9 M / yr |
| Default foreign-turnkey external capital | $11.38 B |
| External capital saved | $10.05 B |
| Capital + lifetime external interest saved | $22.41 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $2.92 B | $438.1 M | $2.48 B |
| Stations | $1.23 B | $246.2 M | $985.0 M |
| Depots | $371.3 M | $92.8 M | $278.5 M |
| Rolling stock | $738.1 M | $258.3 M | $479.8 M |
| Dedicated solar plants | $337.5 M | $151.9 M | $185.6 M |
| Residual train control | $17.5 M | $8.7 M | $8.7 M |
| Charging microgrids | $59.0 M | $23.6 M | $35.4 M |
| EPC / project services | $391.5 M | $58.7 M | $332.8 M |
| Shared national trainset factory | $255.8 M | $51.2 M | $204.7 M |
| **Total** | **$6.32 B** | **$1.33 B** | **$4.99 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [San Salvador](San-Salvador/README.md) | 1,800,000 | 659 | $6.05 B | $1.28 B | $4.77 B |

## Local Basis And Regeneration

Country finance parameters use `SV` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

| City | Current lines | Added residential lines | Original station circles | Current station circles |
| --- | ---: | ---: | ---: | ---: |
| [San Salvador](San-Salvador/README.md) | 21 | 15 | 38.0% | 80.0% |

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
