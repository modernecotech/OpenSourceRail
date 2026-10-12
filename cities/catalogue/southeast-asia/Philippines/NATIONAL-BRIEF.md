# Philippines National OpenSourceRail Strategy

This page contains only Philippines-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$7.87 B (88.7%) of external capital** and **$9.67 B of external interest**. Capital plus saved interest totals **$17.54 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 1,827,000 |
| Trainsets / vehicle modules | 379 / 1,516 |
| City infrastructure and fleet CAPEX | $4.53 B |
| Shared national factory | $369.9 M |
| Factory sizing basis | 1,516 modules for Davao, then reused nationally |
| **Total national programme** | **$4.93 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.00 B (20.3%) |
| Domestic / local capital | $3.93 B (79.7%) |
| Annual external capital draw | $200.3 M / yr |
| Annual local capital draw | $785.0 M / yr |
| Annual public construction commitment | $396.8 M / yr for 5 years |
| Annual post-grace debt service | $279.0 M / yr |
| Default foreign-turnkey external capital | $8.87 B |
| External capital saved | $7.87 B |
| Capital + lifetime external interest saved | $17.54 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $2.68 B | $401.8 M | $2.28 B |
| Stations | $602.9 M | $120.6 M | $482.3 M |
| Depots | $177.5 M | $44.4 M | $133.1 M |
| Rolling stock | $424.5 M | $148.6 M | $275.9 M |
| Dedicated solar plants | $328.8 M | $147.9 M | $180.8 M |
| Residual train control | $14.9 M | $7.5 M | $7.5 M |
| Charging microgrids | $28.7 M | $11.5 M | $17.2 M |
| EPC / project services | $300.8 M | $45.1 M | $255.7 M |
| Shared national trainset factory | $369.9 M | $74.0 M | $295.9 M |
| **Total** | **$4.93 B** | **$1.00 B** | **$3.93 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital | Lines | Added lines | Original circles | Current circles |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| [Davao](Davao/README.md) | 1,827,000 | 379 | $4.53 B | $923.4 M | $3.61 B | 9 | 3 | 42.8% | 40.5% |

## Local Basis And Regeneration

Country finance parameters use `PH` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
