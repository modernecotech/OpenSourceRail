# Bolivia National OpenSourceRail Strategy

This page contains only Bolivia-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$7.41 B (88.8%) of external capital** and **$9.12 B of external interest**. Capital plus saved interest totals **$16.53 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 1,815,000 |
| Trainsets / vehicle modules | 317 / 1,268 |
| City infrastructure and fleet CAPEX | $3.75 B |
| Shared national factory | $827.2 M |
| Factory sizing basis | 1,268 modules for La Paz, then reused nationally |
| **Total national programme** | **$4.64 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $931.1 M (20.1%) |
| Domestic / local capital | $3.71 B (79.9%) |
| Annual external capital draw | $186.2 M / yr |
| Annual local capital draw | $741.0 M / yr |
| Annual public construction commitment | $501.3 M / yr for 5 years |
| Annual post-grace debt service | $374.3 M / yr |
| Default foreign-turnkey external capital | $8.35 B |
| External capital saved | $7.41 B |
| Capital + lifetime external interest saved | $16.53 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $2.28 B | $341.4 M | $1.93 B |
| Stations | $443.6 M | $88.7 M | $354.9 M |
| Depots | $164.1 M | $41.0 M | $123.1 M |
| Rolling stock | $355.0 M | $124.3 M | $230.8 M |
| Dedicated solar plants | $251.6 M | $113.2 M | $138.4 M |
| Residual train control | $11.8 M | $5.9 M | $5.9 M |
| Charging microgrids | $20.3 M | $8.1 M | $12.2 M |
| EPC / project services | $286.9 M | $43.0 M | $243.8 M |
| Shared national trainset factory | $827.2 M | $165.4 M | $661.8 M |
| **Total** | **$4.64 B** | **$931.1 M** | **$3.71 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital | Lines | Added lines | Original circles | Current circles |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| [La Paz](La-Paz/README.md) | 1,815,000 | 317 | $3.75 B | $757.0 M | $2.99 B | 9 | 3 | 39.0% | 37.3% |

## Local Basis And Regeneration

Country finance parameters use `BO` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
