# Niger National OpenSourceRail Strategy

This page contains only Niger-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$6.63 B (89.0%) of external capital** and **$8.56 B of external interest**. Capital plus saved interest totals **$15.19 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 1,407,635 |
| Trainsets / vehicle modules | 284 / 1,136 |
| City infrastructure and fleet CAPEX | $3.20 B |
| Shared national factory | $875.6 M |
| Factory sizing basis | 1,136 modules for Niamey, then reused nationally |
| **Total national programme** | **$4.14 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $818.6 M (19.8%) |
| Domestic / local capital | $3.32 B (80.2%) |
| Annual external capital draw | $81.9 M / yr |
| Annual local capital draw | $331.7 M / yr |
| Annual public construction commitment | $342.0 M / yr for 10 years |
| Annual post-grace debt service | $308.6 M / yr |
| Default foreign-turnkey external capital | $7.44 B |
| External capital saved | $6.63 B |
| Capital + lifetime external interest saved | $15.19 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $1.78 B | $267.3 M | $1.51 B |
| Stations | $582.1 M | $116.4 M | $465.7 M |
| Depots | $160.0 M | $40.0 M | $120.0 M |
| Rolling stock | $318.1 M | $111.3 M | $206.8 M |
| Dedicated solar plants | $120.4 M | $54.2 M | $66.2 M |
| Residual train control | $9.4 M | $4.7 M | $4.7 M |
| Charging microgrids | $25.4 M | $10.2 M | $15.3 M |
| EPC / project services | $262.7 M | $39.4 M | $223.3 M |
| Shared national trainset factory | $875.6 M | $175.1 M | $700.5 M |
| **Total** | **$4.14 B** | **$818.6 M** | **$3.32 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital | Lines | Added lines | Original circles | Current circles |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| [Niamey](Niamey/README.md) | 1,407,635 | 284 | $3.20 B | $634.3 M | $2.56 B | 9 | 3 | 35.0% | 31.3% |

## Local Basis And Regeneration

Country finance parameters use `NE` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
