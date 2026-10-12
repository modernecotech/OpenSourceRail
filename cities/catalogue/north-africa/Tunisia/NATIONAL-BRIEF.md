# Tunisia National OpenSourceRail Strategy

This page contains only Tunisia-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$7.17 B (88.9%) of external capital** and **$8.82 B of external interest**. Capital plus saved interest totals **$15.99 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 2,900,000 |
| Trainsets / vehicle modules | 344 / 1,376 |
| City infrastructure and fleet CAPEX | $3.99 B |
| Shared national factory | $457.2 M |
| Factory sizing basis | 1,376 modules for Tunis, then reused nationally |
| **Total national programme** | **$4.48 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $896.6 M (20.0%) |
| Domestic / local capital | $3.59 B (80.0%) |
| Annual external capital draw | $179.3 M / yr |
| Annual local capital draw | $717.1 M / yr |
| Annual public construction commitment | $441.9 M / yr for 5 years |
| Annual post-grace debt service | $322.8 M / yr |
| Default foreign-turnkey external capital | $8.07 B |
| External capital saved | $7.17 B |
| Capital + lifetime external interest saved | $15.99 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $2.46 B | $368.8 M | $2.09 B |
| Stations | $457.4 M | $91.5 M | $365.9 M |
| Depots | $159.4 M | $39.8 M | $119.5 M |
| Rolling stock | $385.3 M | $134.8 M | $250.4 M |
| Dedicated solar plants | $250.2 M | $112.6 M | $137.6 M |
| Residual train control | $13.4 M | $6.7 M | $6.7 M |
| Charging microgrids | $23.3 M | $9.3 M | $14.0 M |
| EPC / project services | $276.8 M | $41.5 M | $235.3 M |
| Shared national trainset factory | $457.2 M | $91.4 M | $365.8 M |
| **Total** | **$4.48 B** | **$896.6 M** | **$3.59 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital | Lines | Added lines | Original circles | Current circles |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| [Tunis](Tunis/README.md) | 2,900,000 | 344 | $3.99 B | $800.4 M | $3.19 B | 8 | 3 | 35.0% | 32.8% |

## Local Basis And Regeneration

Country finance parameters use `TN` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
