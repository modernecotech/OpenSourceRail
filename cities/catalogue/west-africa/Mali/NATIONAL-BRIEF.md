# Mali National OpenSourceRail Strategy

This page contains only Mali-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$10.40 B (89.3%) of external capital** and **$13.43 B of external interest**. Capital plus saved interest totals **$23.83 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 2,929,000 |
| Trainsets / vehicle modules | 474 / 1,896 |
| City infrastructure and fleet CAPEX | $6.17 B |
| Shared national factory | $280.8 M |
| Factory sizing basis | 1,896 modules for Bamako, then reused nationally |
| **Total national programme** | **$6.47 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.25 B (19.3%) |
| Domestic / local capital | $5.22 B (80.7%) |
| Annual external capital draw | $124.9 M / yr |
| Annual local capital draw | $522.1 M / yr |
| Annual public construction commitment | $557.5 M / yr for 10 years |
| Annual post-grace debt service | $501.4 M / yr |
| Default foreign-turnkey external capital | $11.65 B |
| External capital saved | $10.40 B |
| Capital + lifetime external interest saved | $23.83 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $3.60 B | $540.7 M | $3.06 B |
| Stations | $1.18 B | $235.2 M | $940.6 M |
| Depots | $195.8 M | $49.0 M | $146.9 M |
| Rolling stock | $530.9 M | $185.8 M | $345.1 M |
| Dedicated solar plants | $207.6 M | $93.4 M | $114.2 M |
| Residual train control | $15.6 M | $7.8 M | $7.8 M |
| Charging microgrids | $50.0 M | $20.0 M | $30.0 M |
| EPC / project services | $409.7 M | $61.5 M | $348.3 M |
| Shared national trainset factory | $280.8 M | $56.2 M | $224.7 M |
| **Total** | **$6.47 B** | **$1.25 B** | **$5.22 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital | Lines | Added lines | Original circles | Current circles |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| [Bamako](Bamako/README.md) | 2,929,000 | 474 | $6.17 B | $1.19 B | $4.98 B | 9 | 3 | 40.3% | 48.9% |

## Local Basis And Regeneration

Country finance parameters use `ML` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
