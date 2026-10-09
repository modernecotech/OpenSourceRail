# Lebanon National OpenSourceRail Strategy

This page contains only Lebanon-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$7.77 B (88.6%) of external capital** and **$9.84 B of external interest**. Capital plus saved interest totals **$17.60 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 3 |
| Represented population | 3,230,000 |
| Trainsets / vehicle modules | 576 / 1,888 |
| City infrastructure and fleet CAPEX | $4.02 B |
| Shared national factory | $794.6 M |
| Factory sizing basis | 1,028 modules for Beirut, then reused nationally |
| **Total national programme** | **$4.87 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $999.6 M (20.5%) |
| Domestic / local capital | $3.87 B (79.5%) |
| Annual external capital draw | $124.9 M / yr |
| Annual local capital draw | $484.0 M / yr |
| Annual public construction commitment | $916.1 M / yr for 8 years |
| Annual post-grace debt service | $834.5 M / yr |
| Default foreign-turnkey external capital | $8.77 B |
| External capital saved | $7.77 B |
| Capital + lifetime external interest saved | $17.60 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $1.98 B | $297.5 M | $1.69 B |
| Stations | $732.6 M | $146.5 M | $586.1 M |
| Depots | $337.6 M | $84.4 M | $253.2 M |
| Rolling stock | $542.0 M | $189.7 M | $352.3 M |
| Dedicated solar plants | $130.1 M | $58.5 M | $71.5 M |
| Residual train control | $11.7 M | $5.8 M | $5.8 M |
| Charging microgrids | $29.1 M | $11.7 M | $17.5 M |
| EPC / project services | $310.2 M | $46.5 M | $263.6 M |
| Shared national trainset factory | $794.6 M | $158.9 M | $635.7 M |
| **Total** | **$4.87 B** | **$999.6 M** | **$3.87 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Beirut](Beirut/README.md) | 2,200,000 | 257 | $2.34 B | $487.0 M | $1.85 B |
| [Tripoli Lb](Tripoli-Lb/README.md) | 730,000 | 222 | $1.11 B | $234.6 M | $875.1 M |
| [Sidon](Sidon/README.md) | 300,000 | 97 | $570.0 M | $110.8 M | $459.3 M |

## Local Basis And Regeneration

Country finance parameters use `LB` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

| City | Current lines | Added residential lines | Original station circles | Current station circles |
| --- | ---: | ---: | ---: | ---: |
| [Beirut](Beirut/README.md) | 8 | 2 | 61.8% | 81.1% |
| [Sidon](Sidon/README.md) | 6 | 3 | 48.5% | 69.8% |
| [Tripoli Lb](Tripoli-Lb/README.md) | 7 | 4 | 34.6% | 79.1% |

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
