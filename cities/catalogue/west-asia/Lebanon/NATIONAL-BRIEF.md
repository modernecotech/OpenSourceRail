# Lebanon National OpenSourceRail Strategy

This page contains only Lebanon-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$8.50 B (88.9%) of external capital** and **$10.76 B of external interest**. Capital plus saved interest totals **$19.27 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 3 |
| Represented population | 3,230,000 |
| Trainsets / vehicle modules | 520 / 1,739 |
| City infrastructure and fleet CAPEX | $4.45 B |
| Shared national factory | $811.1 M |
| Factory sizing basis | 1,052 modules for Beirut, then reused nationally |
| **Total national programme** | **$5.31 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.06 B (20.0%) |
| Domestic / local capital | $4.25 B (80.0%) |
| Annual external capital draw | $132.9 M / yr |
| Annual local capital draw | $531.4 M / yr |
| Annual public construction commitment | $1.00 B / yr for 8 years |
| Annual post-grace debt service | $914.3 M / yr |
| Default foreign-turnkey external capital | $9.57 B |
| External capital saved | $8.50 B |
| Capital + lifetime external interest saved | $19.27 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $2.49 B | $373.6 M | $2.12 B |
| Stations | $683.0 M | $136.6 M | $546.4 M |
| Depots | $282.6 M | $70.6 M | $211.9 M |
| Rolling stock | $497.3 M | $174.1 M | $323.2 M |
| Dedicated solar plants | $174.8 M | $78.7 M | $96.1 M |
| Residual train control | $12.9 M | $6.4 M | $6.4 M |
| Charging microgrids | $25.9 M | $10.3 M | $15.5 M |
| EPC / project services | $336.2 M | $50.4 M | $285.8 M |
| Shared national trainset factory | $811.1 M | $162.2 M | $648.8 M |
| **Total** | **$5.31 B** | **$1.06 B** | **$4.25 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital | Lines | Added lines | Original circles | Current circles |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| [Beirut](Beirut/README.md) | 2,200,000 | 263 | $2.89 B | $583.5 M | $2.31 B | 9 | 3 | 61.8% | 64.5% |
| [Tripoli Lb](Tripoli-Lb/README.md) | 730,000 | 173 | $952.9 M | $197.5 M | $755.3 M | 4 | 1 | 34.6% | 62.8% |
| [Sidon](Sidon/README.md) | 300,000 | 84 | $600.4 M | $111.3 M | $489.1 M | 4 | 1 | 48.5% | 68.8% |

## Local Basis And Regeneration

Country finance parameters use `LB` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
