# Sri Lanka National OpenSourceRail Strategy

This page contains only Sri Lanka-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$18.65 B (87.9%) of external capital** and **$23.38 B of external interest**. Capital plus saved interest totals **$42.03 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 4 |
| Represented population | 7,398,000 |
| Trainsets / vehicle modules | 1,371 / 6,069 |
| City infrastructure and fleet CAPEX | $10.98 B |
| Shared national factory | $759.7 M |
| Factory sizing basis | 3,912 modules for Colombo, then reused nationally |
| **Total national programme** | **$11.79 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $2.57 B (21.8%) |
| Domestic / local capital | $9.22 B (78.2%) |
| Annual external capital draw | $367.5 M / yr |
| Annual local capital draw | $1.32 B / yr |
| Annual public construction commitment | $1.37 B / yr for 7 years |
| Annual post-grace debt service | $1.16 B / yr |
| Default foreign-turnkey external capital | $21.22 B |
| External capital saved | $18.65 B |
| Capital + lifetime external interest saved | $42.03 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $5.39 B | $807.8 M | $4.58 B |
| Stations | $1.66 B | $331.2 M | $1.32 B |
| Depots | $609.4 M | $152.4 M | $457.1 M |
| Rolling stock | $1.74 B | $609.9 M | $1.13 B |
| Dedicated solar plants | $814.1 M | $366.3 M | $447.7 M |
| Residual train control | $29.3 M | $14.6 M | $14.6 M |
| Charging microgrids | $75.8 M | $30.3 M | $45.5 M |
| EPC / project services | $718.1 M | $107.7 M | $610.4 M |
| Shared national trainset factory | $759.7 M | $151.9 M | $607.8 M |
| **Total** | **$11.79 B** | **$2.57 B** | **$9.22 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital | Lines | Added lines | Original circles | Current circles |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| [Colombo](Colombo/README.md) | 5,648,000 | 652 | $7.03 B | $1.58 B | $5.45 B | 14 | 5 | 40.2% | 37.9% |
| [Kandy](Kandy/README.md) | 650,000 | 265 | $1.50 B | $312.9 M | $1.18 B | 5 | 2 | 22.2% | 24.9% |
| [Jaffna](Jaffna/README.md) | 600,000 | 212 | $1.15 B | $243.4 M | $906.1 M | 5 | 2 | 25.3% | 40.0% |
| [Galle](Galle/README.md) | 500,000 | 242 | $1.31 B | $275.2 M | $1.03 B | 5 | 2 | 35.1% | 33.8% |

## Local Basis And Regeneration

Country finance parameters use `LK` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
