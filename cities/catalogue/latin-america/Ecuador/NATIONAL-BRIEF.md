# Ecuador National OpenSourceRail Strategy

This page contains only Ecuador-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$4.52 B (88.5%) of external capital** and **$5.56 B of external interest**. Capital plus saved interest totals **$10.08 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 817,100 |
| Trainsets / vehicle modules | 375 / 1,125 |
| City infrastructure and fleet CAPEX | $1.92 B |
| Shared national factory | $863.1 M |
| Factory sizing basis | 1,125 modules for Cuenca, then reused nationally |
| **Total national programme** | **$2.84 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $589.4 M (20.8%) |
| Domestic / local capital | $2.25 B (79.2%) |
| Annual external capital draw | $117.9 M / yr |
| Annual local capital draw | $450.2 M / yr |
| Annual public construction commitment | $287.6 M / yr for 5 years |
| Annual post-grace debt service | $212.3 M / yr |
| Default foreign-turnkey external capital | $5.11 B |
| External capital saved | $4.52 B |
| Capital + lifetime external interest saved | $10.08 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $945.4 M | $141.8 M | $803.6 M |
| Stations | $258.5 M | $51.7 M | $206.8 M |
| Depots | $182.2 M | $45.5 M | $136.6 M |
| Rolling stock | $337.5 M | $118.1 M | $219.4 M |
| Dedicated solar plants | $61.3 M | $27.6 M | $33.7 M |
| Residual train control | $5.3 M | $2.7 M | $2.7 M |
| Charging microgrids | $5.2 M | $2.1 M | $3.1 M |
| EPC / project services | $181.8 M | $27.3 M | $154.5 M |
| Shared national trainset factory | $863.1 M | $172.6 M | $690.5 M |
| **Total** | **$2.84 B** | **$589.4 M** | **$2.25 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Cuenca](Cuenca/README.md) | 817,100 | 375 | $1.92 B | $407.7 M | $1.51 B |

## Local Basis And Regeneration

Country finance parameters use `EC` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

| City | Current lines | Added residential lines | Original station circles | Current station circles |
| --- | ---: | ---: | ---: | ---: |
| [Cuenca](Cuenca/README.md) | 11 | 8 | 34.0% | 78.8% |

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
