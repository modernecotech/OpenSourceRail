# Mali National OpenSourceRail Strategy

This page contains only Mali-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$11.43 B (88.9%) of external capital** and **$14.77 B of external interest**. Capital plus saved interest totals **$26.20 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 2,929,000 |
| Trainsets / vehicle modules | 691 / 2,764 |
| City infrastructure and fleet CAPEX | $6.87 B |
| Shared national factory | $251.4 M |
| Factory sizing basis | 2,764 modules for Bamako, then reused nationally |
| **Total national programme** | **$7.14 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.42 B (19.9%) |
| Domestic / local capital | $5.72 B (80.1%) |
| Annual external capital draw | $142.2 M / yr |
| Annual local capital draw | $572.0 M / yr |
| Annual public construction commitment | $613.1 M / yr for 10 years |
| Annual post-grace debt service | $552.6 M / yr |
| Default foreign-turnkey external capital | $12.86 B |
| External capital saved | $11.43 B |
| Capital + lifetime external interest saved | $26.20 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $3.66 B | $549.5 M | $3.11 B |
| Stations | $1.34 B | $268.7 M | $1.07 B |
| Depots | $388.1 M | $97.0 M | $291.1 M |
| Rolling stock | $773.9 M | $270.9 M | $503.0 M |
| Dedicated solar plants | $185.8 M | $83.6 M | $102.2 M |
| Residual train control | $16.6 M | $8.3 M | $8.3 M |
| Charging microgrids | $64.7 M | $25.9 M | $38.8 M |
| EPC / project services | $455.1 M | $68.3 M | $386.8 M |
| Shared national trainset factory | $251.4 M | $50.3 M | $201.1 M |
| **Total** | **$7.14 B** | **$1.42 B** | **$5.72 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Bamako](Bamako/README.md) | 2,929,000 | 691 | $6.87 B | $1.37 B | $5.50 B |

## Local Basis And Regeneration

Country finance parameters use `ML` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

| City | Current lines | Added residential lines | Original station circles | Current station circles |
| --- | ---: | ---: | ---: | ---: |
| [Bamako](Bamako/README.md) | 22 | 16 | 40.3% | 80.7% |

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
