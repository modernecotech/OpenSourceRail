# Sri Lanka National OpenSourceRail Strategy

This page contains only Sri Lanka-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$30.06 B (87.6%) of external capital** and **$37.68 B of external interest**. Capital plus saved interest totals **$67.74 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 4 |
| Represented population | 7,398,000 |
| Trainsets / vehicle modules | 2,491 / 11,295 |
| City infrastructure and fleet CAPEX | $18.14 B |
| Shared national factory | $863.1 M |
| Factory sizing basis | 7,644 modules for Colombo, then reused nationally |
| **Total national programme** | **$19.06 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $4.25 B (22.3%) |
| Domestic / local capital | $14.81 B (77.7%) |
| Annual external capital draw | $606.7 M / yr |
| Annual local capital draw | $2.12 B / yr |
| Annual public construction commitment | $2.21 B / yr for 7 years |
| Annual post-grace debt service | $1.87 B / yr |
| Default foreign-turnkey external capital | $34.31 B |
| External capital saved | $30.06 B |
| Capital + lifetime external interest saved | $67.74 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $7.17 B | $1.08 B | $6.09 B |
| Stations | $3.94 B | $789.0 M | $3.16 B |
| Depots | $1.46 B | $365.2 M | $1.10 B |
| Rolling stock | $3.24 B | $1.13 B | $2.10 B |
| Dedicated solar plants | $988.6 M | $444.8 M | $543.7 M |
| Residual train control | $42.5 M | $21.3 M | $21.3 M |
| Charging microgrids | $171.4 M | $68.6 M | $102.9 M |
| EPC / project services | $1.18 B | $177.3 M | $1.00 B |
| Shared national trainset factory | $863.1 M | $172.6 M | $690.5 M |
| **Total** | **$19.06 B** | **$4.25 B** | **$14.81 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Colombo](Colombo/README.md) | 5,648,000 | 1,274 | $11.60 B | $2.68 B | $8.92 B |
| [Kandy](Kandy/README.md) | 650,000 | 473 | $2.73 B | $569.1 M | $2.16 B |
| [Jaffna](Jaffna/README.md) | 600,000 | 329 | $1.70 B | $362.7 M | $1.33 B |
| [Galle](Galle/README.md) | 500,000 | 415 | $2.11 B | $450.5 M | $1.66 B |

## Local Basis And Regeneration

Country finance parameters use `LK` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

| City | Current lines | Added residential lines | Original station circles | Current station circles |
| --- | ---: | ---: | ---: | ---: |
| [Colombo](Colombo/README.md) | 37 | 28 | 40.2% | 82.1% |
| [Galle](Galle/README.md) | 15 | 12 | 35.1% | 74.1% |
| [Jaffna](Jaffna/README.md) | 12 | 9 | 25.3% | 74.4% |
| [Kandy](Kandy/README.md) | 18 | 15 | 22.2% | 64.9% |

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
