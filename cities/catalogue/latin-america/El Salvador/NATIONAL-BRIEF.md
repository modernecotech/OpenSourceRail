# El Salvador National OpenSourceRail Strategy

This page contains only El Salvador-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$7.62 B (88.7%) of external capital** and **$9.36 B of external interest**. Capital plus saved interest totals **$16.98 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 1,800,000 |
| Trainsets / vehicle modules | 359 / 1,436 |
| City infrastructure and fleet CAPEX | $4.25 B |
| Shared national factory | $484.4 M |
| Factory sizing basis | 1,436 modules for San Salvador, then reused nationally |
| **Total national programme** | **$4.77 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $966.0 M (20.3%) |
| Domestic / local capital | $3.80 B (79.7%) |
| Annual external capital draw | $193.2 M / yr |
| Annual local capital draw | $760.3 M / yr |
| Annual public construction commitment | $545.2 M / yr for 5 years |
| Annual post-grace debt service | $413.0 M / yr |
| Default foreign-turnkey external capital | $8.58 B |
| External capital saved | $7.62 B |
| Capital + lifetime external interest saved | $16.98 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $2.52 B | $377.4 M | $2.14 B |
| Stations | $560.9 M | $112.2 M | $448.7 M |
| Depots | $173.3 M | $43.3 M | $130.0 M |
| Rolling stock | $402.1 M | $140.7 M | $261.4 M |
| Dedicated solar plants | $299.0 M | $134.6 M | $164.5 M |
| Residual train control | $13.6 M | $6.8 M | $6.8 M |
| Charging microgrids | $25.6 M | $10.2 M | $15.3 M |
| EPC / project services | $292.3 M | $43.8 M | $248.5 M |
| Shared national trainset factory | $484.4 M | $96.9 M | $387.5 M |
| **Total** | **$4.77 B** | **$966.0 M** | **$3.80 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital | Lines | Added lines | Original circles | Current circles |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| [San Salvador](San-Salvador/README.md) | 1,800,000 | 359 | $4.25 B | $864.0 M | $3.39 B | 9 | 3 | 38.0% | 36.5% |

## Local Basis And Regeneration

Country finance parameters use `SV` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
