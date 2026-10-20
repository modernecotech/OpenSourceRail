# Nigeria National OpenSourceRail Strategy

This page contains only Nigeria-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$46.55 B (88.4%) of external capital** and **$58.35 B of external interest**. Capital plus saved interest totals **$104.90 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 10 |
| Represented population | 19,200,000 |
| Trainsets / vehicle modules | 2,829 / 12,934 |
| City infrastructure and fleet CAPEX | $28.31 B |
| Shared national factory | $877.6 M |
| Factory sizing basis | 4,662 modules for Kano, then reused nationally |
| **Total national programme** | **$29.25 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $6.10 B (20.9%) |
| Domestic / local capital | $23.15 B (79.1%) |
| Annual external capital draw | $872.1 M / yr |
| Annual local capital draw | $3.31 B / yr |
| Annual public construction commitment | $3.44 B / yr for 7 years |
| Annual post-grace debt service | $2.90 B / yr |
| Default foreign-turnkey external capital | $52.65 B |
| External capital saved | $46.55 B |
| Capital + lifetime external interest saved | $104.90 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $15.19 B | $2.28 B | $12.91 B |
| Stations | $4.33 B | $866.1 M | $3.46 B |
| Depots | $1.43 B | $357.6 M | $1.07 B |
| Rolling stock | $3.66 B | $1.28 B | $2.38 B |
| Dedicated solar plants | $1.67 B | $752.7 M | $919.9 M |
| Residual train control | $78.9 M | $39.4 M | $39.4 M |
| Charging microgrids | $208.0 M | $83.2 M | $124.8 M |
| EPC / project services | $1.80 B | $270.6 M | $1.53 B |
| Shared national trainset factory | $877.6 M | $175.5 M | $702.1 M |
| **Total** | **$29.25 B** | **$6.10 B** | **$23.15 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital | Lines | Added lines | Original circles | Current circles |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| [Kano](Kano/README.md) | 4,200,000 | 777 | $8.41 B | $1.82 B | $6.59 B | 14 | 5 | 38.8% | 43.0% |
| [Ibadan](Ibadan/README.md) | 3,900,000 | 343 | $3.52 B | $787.1 M | $2.74 B | 8 | 3 | 23.1% | 29.4% |
| [Port Harcourt](Port-Harcourt/README.md) | 3,000,000 | 270 | $3.38 B | $680.0 M | $2.70 B | 8 | 3 | 23.8% | 25.8% |
| [Benin City](Benin-City/README.md) | 1,800,000 | 286 | $2.77 B | $576.5 M | $2.19 B | 8 | 3 | 34.4% | 34.9% |
| [Onitsha](Onitsha/README.md) | 1,500,000 | 278 | $3.46 B | $694.3 M | $2.77 B | 8 | 3 | 25.1% | 29.5% |
| [Maiduguri](Maiduguri/README.md) | 1,200,000 | 253 | $3.23 B | $623.9 M | $2.61 B | 8 | 3 | 30.7% | 36.8% |
| [Ilorin](Ilorin/README.md) | 1,000,000 | 180 | $1.01 B | $211.6 M | $802.2 M | 5 | 2 | 20.9% | 24.7% |
| [Aba Ng](Aba-Ng/README.md) | 900,000 | 115 | $673.8 M | $139.8 M | $534.0 M | 4 | 1 | 27.2% | 30.0% |
| [Jos](Jos/README.md) | 900,000 | 203 | $1.11 B | $229.4 M | $883.0 M | 5 | 2 | 21.6% | 28.9% |
| [Uyo](Uyo/README.md) | 800,000 | 124 | $735.8 M | $152.9 M | $582.8 M | 4 | 1 | 14.7% | 17.9% |

## Local Basis And Regeneration

Country finance parameters use `NG` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
