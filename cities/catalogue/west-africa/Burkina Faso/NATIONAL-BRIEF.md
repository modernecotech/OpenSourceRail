# Burkina Faso National OpenSourceRail Strategy

This page contains only Burkina Faso-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$7.30 B (88.9%) of external capital** and **$9.43 B of external interest**. Capital plus saved interest totals **$16.73 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 2,531,000 |
| Trainsets / vehicle modules | 351 / 1,404 |
| City infrastructure and fleet CAPEX | $3.78 B |
| Shared national factory | $735.7 M |
| Factory sizing basis | 1,404 modules for Ouagadougou, then reused nationally |
| **Total national programme** | **$4.56 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $912.0 M (20.0%) |
| Domestic / local capital | $3.65 B (80.0%) |
| Annual external capital draw | $91.2 M / yr |
| Annual local capital draw | $365.1 M / yr |
| Annual public construction commitment | $391.5 M / yr for 10 years |
| Annual post-grace debt service | $353.0 M / yr |
| Default foreign-turnkey external capital | $8.21 B |
| External capital saved | $7.30 B |
| Capital + lifetime external interest saved | $16.73 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $2.06 B | $309.6 M | $1.75 B |
| Stations | $707.9 M | $141.6 M | $566.3 M |
| Depots | $172.6 M | $43.2 M | $129.5 M |
| Rolling stock | $393.1 M | $137.6 M | $255.5 M |
| Dedicated solar plants | $159.0 M | $71.6 M | $87.5 M |
| Residual train control | $11.6 M | $5.8 M | $5.8 M |
| Charging microgrids | $30.8 M | $12.3 M | $18.5 M |
| EPC / project services | $288.1 M | $43.2 M | $244.9 M |
| Shared national trainset factory | $735.7 M | $147.1 M | $588.6 M |
| **Total** | **$4.56 B** | **$912.0 M** | **$3.65 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital | Lines | Added lines | Original circles | Current circles |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| [Ouagadougou](Ouagadougou/README.md) | 2,531,000 | 351 | $3.78 B | $757.1 M | $3.02 B | 9 | 3 | 29.1% | 24.3% |

## Local Basis And Regeneration

Country finance parameters use `BF` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
