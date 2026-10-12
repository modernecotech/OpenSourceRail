# South Africa National OpenSourceRail Strategy

This page contains only South Africa-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$23.47 B (88.0%) of external capital** and **$28.85 B of external interest**. Capital plus saved interest totals **$52.32 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 5 |
| Represented population | 6,200,000 |
| Trainsets / vehicle modules | 1,674 / 7,370 |
| City infrastructure and fleet CAPEX | $13.90 B |
| Shared national factory | $863.1 M |
| Factory sizing basis | 4,872 modules for Durban, then reused nationally |
| **Total national programme** | **$14.82 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $3.21 B (21.7%) |
| Domestic / local capital | $11.61 B (78.3%) |
| Annual external capital draw | $642.5 M / yr |
| Annual local capital draw | $2.32 B / yr |
| Annual public construction commitment | $1.58 B / yr for 5 years |
| Annual post-grace debt service | $1.19 B / yr |
| Default foreign-turnkey external capital | $26.68 B |
| External capital saved | $23.47 B |
| Capital + lifetime external interest saved | $52.32 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $6.85 B | $1.03 B | $5.82 B |
| Stations | $2.24 B | $447.0 M | $1.79 B |
| Depots | $718.3 M | $179.6 M | $538.8 M |
| Rolling stock | $2.11 B | $738.5 M | $1.37 B |
| Dedicated solar plants | $1.02 B | $457.5 M | $559.2 M |
| Residual train control | $36.2 M | $18.1 M | $18.1 M |
| Charging microgrids | $91.5 M | $36.6 M | $54.9 M |
| EPC / project services | $903.1 M | $135.5 M | $767.6 M |
| Shared national trainset factory | $863.1 M | $172.6 M | $690.5 M |
| **Total** | **$14.82 B** | **$3.21 B** | **$11.61 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital | Lines | Added lines | Original circles | Current circles |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| [Durban](Durban/README.md) | 3,900,000 | 812 | $9.05 B | $2.01 B | $7.03 B | 14 | 5 | 28.1% | 31.0% |
| [East London Za](East-London-Za/README.md) | 800,000 | 221 | $1.25 B | $265.1 M | $989.0 M | 5 | 2 | 34.3% | 35.6% |
| [Bloemfontein](Bloemfontein/README.md) | 600,000 | 354 | $1.92 B | $415.4 M | $1.50 B | 5 | 2 | 39.1% | 51.5% |
| [Polokwane](Polokwane/README.md) | 600,000 | 199 | $1.03 B | $214.5 M | $812.1 M | 5 | 2 | 23.0% | 36.5% |
| [Nelspruit](Nelspruit/README.md) | 300,000 | 88 | $653.6 M | $122.4 M | $531.1 M | 4 | 1 | 40.1% | 37.8% |

## Local Basis And Regeneration

Country finance parameters use `ZA` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
