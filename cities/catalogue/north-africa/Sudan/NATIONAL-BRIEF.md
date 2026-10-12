# Sudan National OpenSourceRail Strategy

This page contains only Sudan-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$28.06 B (88.4%) of external capital** and **$36.25 B of external interest**. Capital plus saved interest totals **$64.31 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 6 |
| Represented population | 10,729,000 |
| Trainsets / vehicle modules | 1,820 / 8,287 |
| City infrastructure and fleet CAPEX | $17.10 B |
| Shared national factory | $507.2 M |
| Factory sizing basis | 4,584 modules for Khartoum, then reused nationally |
| **Total national programme** | **$17.64 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $3.70 B (21.0%) |
| Domestic / local capital | $13.95 B (79.0%) |
| Annual external capital draw | $369.6 M / yr |
| Annual local capital draw | $1.39 B / yr |
| Annual public construction commitment | $2.12 B / yr for 10 years |
| Annual post-grace debt service | $1.93 B / yr |
| Default foreign-turnkey external capital | $31.76 B |
| External capital saved | $28.06 B |
| Capital + lifetime external interest saved | $64.31 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $8.98 B | $1.35 B | $7.64 B |
| Stations | $2.73 B | $546.8 M | $2.19 B |
| Depots | $849.2 M | $212.3 M | $636.9 M |
| Rolling stock | $2.35 B | $823.1 M | $1.53 B |
| Dedicated solar plants | $947.5 M | $426.4 M | $521.1 M |
| Residual train control | $47.3 M | $23.6 M | $23.6 M |
| Charging microgrids | $128.0 M | $51.2 M | $76.8 M |
| EPC / project services | $1.09 B | $163.8 M | $928.3 M |
| Shared national trainset factory | $507.2 M | $101.4 M | $405.8 M |
| **Total** | **$17.64 B** | **$3.70 B** | **$13.95 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital | Lines | Added lines | Original circles | Current circles |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| [Khartoum](Khartoum/README.md) | 5,829,000 | 764 | $8.48 B | $1.84 B | $6.64 B | 14 | 5 | 22.4% | 22.4% |
| [Omdurman](Omdurman/README.md) | 2,800,000 | 535 | $5.51 B | $1.12 B | $4.39 B | 9 | 3 | 24.5% | 23.3% |
| [Nyala](Nyala/README.md) | 600,000 | 164 | $1.01 B | $203.7 M | $811.1 M | 5 | 2 | 18.4% | 19.3% |
| [El Obeid](El-Obeid/README.md) | 500,000 | 166 | $908.4 M | $188.1 M | $720.3 M | 5 | 2 | 18.7% | 24.6% |
| [Kassala](Kassala/README.md) | 500,000 | 86 | $584.4 M | $114.5 M | $469.8 M | 4 | 1 | 21.7% | 21.6% |
| [Port Sudan](Port-Sudan/README.md) | 500,000 | 105 | $598.1 M | $121.7 M | $476.4 M | 4 | 1 | 18.2% | 19.4% |

## Local Basis And Regeneration

Country finance parameters use `SD` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
