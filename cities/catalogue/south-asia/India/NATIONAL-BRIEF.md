# India National OpenSourceRail Strategy

This page contains only India-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$100.06 B (88.5%) of external capital** and **$123.02 B of external interest**. Capital plus saved interest totals **$223.09 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 17 |
| Represented population | 36,304,000 |
| Trainsets / vehicle modules | 5,271 / 25,196 |
| City infrastructure and fleet CAPEX | $61.88 B |
| Shared national factory | $854.7 M |
| Factory sizing basis | 3,198 modules for Kanpur, then reused nationally |
| **Total national programme** | **$62.79 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $12.97 B (20.6%) |
| Domestic / local capital | $49.83 B (79.4%) |
| Annual external capital draw | $2.59 B / yr |
| Annual local capital draw | $9.97 B / yr |
| Annual public construction commitment | $5.45 B / yr for 5 years |
| Annual post-grace debt service | $3.89 B / yr |
| Default foreign-turnkey external capital | $113.03 B |
| External capital saved | $100.06 B |
| Capital + lifetime external interest saved | $223.09 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $35.00 B | $5.25 B | $29.75 B |
| Stations | $8.92 B | $1.78 B | $7.13 B |
| Depots | $2.39 B | $597.8 M | $1.79 B |
| Rolling stock | $7.05 B | $2.47 B | $4.59 B |
| Dedicated solar plants | $4.09 B | $1.84 B | $2.25 B |
| Residual train control | $181.0 M | $90.5 M | $90.5 M |
| Charging microgrids | $466.0 M | $186.4 M | $279.6 M |
| EPC / project services | $3.84 B | $576.0 M | $3.26 B |
| Shared national trainset factory | $854.7 M | $170.9 M | $683.8 M |
| **Total** | **$62.79 B** | **$12.97 B** | **$49.83 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Lucknow](Lucknow/README.md) | 3,500,000 | 508 | $5.62 B | $1.22 B | $4.40 B |
| [Indore](Indore/README.md) | 3,200,000 | 516 | $5.48 B | $1.21 B | $4.28 B |
| [Kanpur](Kanpur/README.md) | 3,200,000 | 533 | $6.44 B | $1.38 B | $5.07 B |
| [Coimbatore](Coimbatore/README.md) | 3,084,000 | 499 | $5.50 B | $1.24 B | $4.26 B |
| [Patna](Patna/README.md) | 2,520,000 | 618 | $7.21 B | $1.46 B | $5.76 B |
| [Bhopal](Bhopal/README.md) | 2,400,000 | 225 | $2.66 B | $525.7 M | $2.13 B |
| [Visakhapatnam](Visakhapatnam/README.md) | 2,300,000 | 276 | $3.19 B | $653.3 M | $2.54 B |
| [Vadodara](Vadodara/README.md) | 2,200,000 | 195 | $2.00 B | $405.4 M | $1.60 B |
| [Rajkot](Rajkot/README.md) | 1,800,000 | 155 | $2.00 B | $386.3 M | $1.61 B |
| [Agra](Agra/README.md) | 1,700,000 | 182 | $2.36 B | $458.2 M | $1.90 B |
| [Madurai](Madurai/README.md) | 1,600,000 | 262 | $3.12 B | $633.2 M | $2.48 B |
| [Meerut](Meerut/README.md) | 1,600,000 | 150 | $1.93 B | $377.3 M | $1.55 B |
| [Raipur](Raipur/README.md) | 1,500,000 | 202 | $2.17 B | $446.4 M | $1.72 B |
| [Varanasi](Varanasi/README.md) | 1,500,000 | 250 | $3.37 B | $647.7 M | $2.72 B |
| [Vijayawada](Vijayawada/README.md) | 1,500,000 | 245 | $3.02 B | $611.3 M | $2.41 B |
| [Ranchi](Ranchi/README.md) | 1,400,000 | 264 | $3.13 B | $634.8 M | $2.49 B |
| [Jodhpur](Jodhpur/README.md) | 1,300,000 | 191 | $2.68 B | $510.4 M | $2.17 B |

## Local Basis And Regeneration

Country finance parameters use `IN` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

| City | Current lines | Added residential lines | Original station circles | Current station circles |
| --- | ---: | ---: | ---: | ---: |
| [Agra](Agra/README.md) | 5 | 0 | Unavailable | Unavailable |
| [Bhopal](Bhopal/README.md) | 6 | 0 | Unavailable | Unavailable |
| [Coimbatore](Coimbatore/README.md) | 9 | 0 | Unavailable | Unavailable |
| [Indore](Indore/README.md) | 8 | 0 | Unavailable | Unavailable |
| [Jodhpur](Jodhpur/README.md) | 5 | 0 | Unavailable | Unavailable |
| [Kanpur](Kanpur/README.md) | 8 | 0 | Unavailable | Unavailable |
| [Lucknow](Lucknow/README.md) | 8 | 0 | Unavailable | Unavailable |
| [Madurai](Madurai/README.md) | 6 | 0 | Unavailable | Unavailable |
| [Meerut](Meerut/README.md) | 4 | 0 | Unavailable | Unavailable |
| [Patna](Patna/README.md) | 6 | 0 | Unavailable | Unavailable |
| [Raipur](Raipur/README.md) | 6 | 0 | Unavailable | Unavailable |
| [Rajkot](Rajkot/README.md) | 5 | 0 | Unavailable | Unavailable |
| [Ranchi](Ranchi/README.md) | 6 | 0 | Unavailable | Unavailable |
| [Vadodara](Vadodara/README.md) | 6 | 0 | Unavailable | Unavailable |
| [Varanasi](Varanasi/README.md) | 6 | 0 | Unavailable | Unavailable |
| [Vijayawada](Vijayawada/README.md) | 6 | 0 | Unavailable | Unavailable |
| [Visakhapatnam](Visakhapatnam/README.md) | 6 | 0 | Unavailable | Unavailable |

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
