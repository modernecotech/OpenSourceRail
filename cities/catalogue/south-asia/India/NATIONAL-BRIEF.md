# India National OpenSourceRail Strategy

This page contains only India-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$107.89 B (88.5%) of external capital** and **$132.64 B of external interest**. Capital plus saved interest totals **$240.53 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 17 |
| Represented population | 36,304,000 |
| Trainsets / vehicle modules | 5,657 / 27,138 |
| City infrastructure and fleet CAPEX | $66.79 B |
| Shared national factory | $865.5 M |
| Factory sizing basis | 3,636 modules for Coimbatore, then reused nationally |
| **Total national programme** | **$67.71 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $13.99 B (20.7%) |
| Domestic / local capital | $53.72 B (79.3%) |
| Annual external capital draw | $2.80 B / yr |
| Annual local capital draw | $10.74 B / yr |
| Annual public construction commitment | $5.87 B / yr for 5 years |
| Annual post-grace debt service | $4.19 B / yr |
| Default foreign-turnkey external capital | $121.88 B |
| External capital saved | $107.89 B |
| Capital + lifetime external interest saved | $240.53 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $37.80 B | $5.67 B | $32.13 B |
| Stations | $9.65 B | $1.93 B | $7.72 B |
| Depots | $2.48 B | $619.0 M | $1.86 B |
| Rolling stock | $7.60 B | $2.66 B | $4.94 B |
| Dedicated solar plants | $4.52 B | $2.03 B | $2.49 B |
| Residual train control | $196.7 M | $98.4 M | $98.4 M |
| Charging microgrids | $468.9 M | $187.6 M | $281.4 M |
| EPC / project services | $4.13 B | $620.1 M | $3.51 B |
| Shared national trainset factory | $865.5 M | $173.1 M | $692.4 M |
| **Total** | **$67.71 B** | **$13.99 B** | **$53.72 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital | Lines | Added lines | Original circles | Current circles |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| [Lucknow](Lucknow/README.md) | 3,500,000 | 532 | $6.05 B | $1.31 B | $4.74 B | 8 | 0 | Unavailable | Unavailable |
| [Indore](Indore/README.md) | 3,200,000 | 581 | $6.17 B | $1.36 B | $4.81 B | 8 | 0 | Unavailable | Unavailable |
| [Kanpur](Kanpur/README.md) | 3,200,000 | 536 | $6.35 B | $1.36 B | $4.99 B | 8 | 0 | Unavailable | Unavailable |
| [Coimbatore](Coimbatore/README.md) | 3,084,000 | 606 | $6.58 B | $1.47 B | $5.11 B | 9 | 0 | Unavailable | Unavailable |
| [Patna](Patna/README.md) | 2,520,000 | 473 | $5.94 B | $1.19 B | $4.75 B | 6 | 0 | Unavailable | Unavailable |
| [Bhopal](Bhopal/README.md) | 2,400,000 | 281 | $3.29 B | $656.5 M | $2.64 B | 6 | 0 | Unavailable | Unavailable |
| [Visakhapatnam](Visakhapatnam/README.md) | 2,300,000 | 326 | $3.91 B | $793.1 M | $3.11 B | 6 | 0 | Unavailable | Unavailable |
| [Vadodara](Vadodara/README.md) | 2,200,000 | 233 | $2.63 B | $526.9 M | $2.11 B | 6 | 0 | Unavailable | Unavailable |
| [Rajkot](Rajkot/README.md) | 1,800,000 | 153 | $1.97 B | $382.3 M | $1.59 B | 5 | 0 | Unavailable | Unavailable |
| [Agra](Agra/README.md) | 1,700,000 | 191 | $2.52 B | $488.7 M | $2.03 B | 5 | 0 | Unavailable | Unavailable |
| [Madurai](Madurai/README.md) | 1,600,000 | 295 | $3.49 B | $708.8 M | $2.78 B | 6 | 0 | Unavailable | Unavailable |
| [Meerut](Meerut/README.md) | 1,600,000 | 184 | $2.28 B | $447.1 M | $1.83 B | 4 | 0 | Unavailable | Unavailable |
| [Raipur](Raipur/README.md) | 1,500,000 | 195 | $2.20 B | $450.6 M | $1.75 B | 6 | 0 | Unavailable | Unavailable |
| [Varanasi](Varanasi/README.md) | 1,500,000 | 270 | $3.59 B | $697.1 M | $2.90 B | 6 | 0 | Unavailable | Unavailable |
| [Vijayawada](Vijayawada/README.md) | 1,500,000 | 254 | $3.18 B | $640.5 M | $2.53 B | 6 | 0 | Unavailable | Unavailable |
| [Ranchi](Ranchi/README.md) | 1,400,000 | 336 | $3.87 B | $787.9 M | $3.08 B | 6 | 0 | Unavailable | Unavailable |
| [Jodhpur](Jodhpur/README.md) | 1,300,000 | 211 | $2.76 B | $534.2 M | $2.23 B | 5 | 0 | Unavailable | Unavailable |

## Local Basis And Regeneration

Country finance parameters use `IN` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
