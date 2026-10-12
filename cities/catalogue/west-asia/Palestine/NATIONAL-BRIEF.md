# Palestine National OpenSourceRail Strategy

This page contains only Palestine-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$6.67 B (88.6%) of external capital** and **$8.36 B of external interest**. Capital plus saved interest totals **$15.02 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 3 |
| Represented population | 1,850,000 |
| Trainsets / vehicle modules | 602 / 1,806 |
| City infrastructure and fleet CAPEX | $3.37 B |
| Shared national factory | $759.7 M |
| Factory sizing basis | 798 modules for Nablus, then reused nationally |
| **Total national programme** | **$4.18 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $858.9 M (20.5%) |
| Domestic / local capital | $3.32 B (79.5%) |
| Annual external capital draw | $122.7 M / yr |
| Annual local capital draw | $474.6 M / yr |
| Annual public construction commitment | $359.5 M / yr for 7 years |
| Annual post-grace debt service | $292.8 M / yr |
| Default foreign-turnkey external capital | $7.53 B |
| External capital saved | $6.67 B |
| Capital + lifetime external interest saved | $15.02 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $1.81 B | $272.2 M | $1.54 B |
| Stations | $426.6 M | $85.3 M | $341.3 M |
| Depots | $238.2 M | $59.5 M | $178.6 M |
| Rolling stock | $541.8 M | $189.6 M | $352.2 M |
| Dedicated solar plants | $117.0 M | $52.7 M | $64.4 M |
| Residual train control | $9.6 M | $4.8 M | $4.8 M |
| Charging microgrids | $7.5 M | $3.0 M | $4.5 M |
| EPC / project services | $265.9 M | $39.9 M | $226.0 M |
| Shared national trainset factory | $759.7 M | $151.9 M | $607.8 M |
| **Total** | **$4.18 B** | **$858.9 M** | **$3.32 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital | Lines | Added lines | Original circles | Current circles |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| [Hebron](Hebron/README.md) | 800,000 | 227 | $1.33 B | $275.1 M | $1.06 B | 4 | 1 | 29.4% | 51.5% |
| [Gaza City](Gaza-City/README.md) | 600,000 | 109 | $579.6 M | $121.3 M | $458.3 M | 4 | 1 | 57.2% | 46.2% |
| [Nablus](Nablus/README.md) | 450,000 | 266 | $1.46 B | $302.6 M | $1.15 B | 5 | 2 | 37.9% | 51.4% |

## Local Basis And Regeneration

Country finance parameters use `PS` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
