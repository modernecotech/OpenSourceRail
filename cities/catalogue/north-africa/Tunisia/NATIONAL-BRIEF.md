# Tunisia National OpenSourceRail Strategy

This page contains only Tunisia-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$11.87 B (88.5%) of external capital** and **$14.60 B of external interest**. Capital plus saved interest totals **$26.47 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 2,900,000 |
| Trainsets / vehicle modules | 793 / 3,172 |
| City infrastructure and fleet CAPEX | $7.18 B |
| Shared national factory | $251.4 M |
| Factory sizing basis | 3,172 modules for Tunis, then reused nationally |
| **Total national programme** | **$7.45 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.54 B (20.7%) |
| Domestic / local capital | $5.91 B (79.3%) |
| Annual external capital draw | $308.3 M / yr |
| Annual local capital draw | $1.18 B / yr |
| Annual public construction commitment | $731.4 M / yr for 5 years |
| Annual post-grace debt service | $535.8 M / yr |
| Default foreign-turnkey external capital | $13.41 B |
| External capital saved | $11.87 B |
| Capital + lifetime external interest saved | $26.47 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $3.50 B | $525.1 M | $2.98 B |
| Stations | $1.42 B | $284.3 M | $1.14 B |
| Depots | $556.9 M | $139.2 M | $417.6 M |
| Rolling stock | $888.2 M | $310.9 M | $577.3 M |
| Dedicated solar plants | $275.9 M | $124.2 M | $151.8 M |
| Residual train control | $20.0 M | $10.0 M | $10.0 M |
| Charging microgrids | $68.4 M | $27.4 M | $41.0 M |
| EPC / project services | $469.5 M | $70.4 M | $399.1 M |
| Shared national trainset factory | $251.4 M | $50.3 M | $201.1 M |
| **Total** | **$7.45 B** | **$1.54 B** | **$5.91 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Tunis](Tunis/README.md) | 2,900,000 | 793 | $7.18 B | $1.49 B | $5.69 B |

## Local Basis And Regeneration

Country finance parameters use `TN` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

| City | Current lines | Added residential lines | Original station circles | Current station circles |
| --- | ---: | ---: | ---: | ---: |
| [Tunis](Tunis/README.md) | 35 | 30 | 35.0% | 79.4% |

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
