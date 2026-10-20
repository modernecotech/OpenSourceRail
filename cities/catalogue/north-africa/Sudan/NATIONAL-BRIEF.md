# Sudan National OpenSourceRail Strategy

This page contains only Sudan-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$28.57 B (88.4%) of external capital** and **$36.90 B of external interest**. Capital plus saved interest totals **$65.47 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 6 |
| Represented population | 10,729,000 |
| Trainsets / vehicle modules | 1,866 / 8,425 |
| City infrastructure and fleet CAPEX | $17.37 B |
| Shared national factory | $554.0 M |
| Factory sizing basis | 4,584 modules for Khartoum, then reused nationally |
| **Total national programme** | **$17.96 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $3.76 B (20.9%) |
| Domestic / local capital | $14.20 B (79.1%) |
| Annual external capital draw | $376.3 M / yr |
| Annual local capital draw | $1.42 B / yr |
| Annual public construction commitment | $2.16 B / yr for 10 years |
| Annual post-grace debt service | $1.96 B / yr |
| Default foreign-turnkey external capital | $32.33 B |
| External capital saved | $28.57 B |
| Capital + lifetime external interest saved | $65.47 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $9.11 B | $1.37 B | $7.74 B |
| Stations | $2.81 B | $561.3 M | $2.25 B |
| Depots | $856.6 M | $214.1 M | $642.4 M |
| Rolling stock | $2.39 B | $837.6 M | $1.56 B |
| Dedicated solar plants | $956.9 M | $430.6 M | $526.3 M |
| Residual train control | $47.9 M | $23.9 M | $23.9 M |
| Charging microgrids | $128.9 M | $51.5 M | $77.3 M |
| EPC / project services | $1.11 B | $166.9 M | $945.6 M |
| Shared national trainset factory | $554.0 M | $110.8 M | $443.2 M |
| **Total** | **$17.96 B** | **$3.76 B** | **$14.20 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital | Lines | Added lines | Original circles | Current circles |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| [Khartoum](Khartoum/README.md) | 5,829,000 | 764 | $8.48 B | $1.84 B | $6.64 B | 14 | 5 | 22.4% | 22.4% |
| [Omdurman](Omdurman/README.md) | 2,800,000 | 535 | $5.51 B | $1.12 B | $4.39 B | 9 | 3 | 24.5% | 23.3% |
| [Nyala](Nyala/README.md) | 600,000 | 164 | $1.01 B | $203.7 M | $811.1 M | 5 | 2 | 18.4% | 19.3% |
| [El Obeid](El-Obeid/README.md) | 500,000 | 184 | $1.01 B | $208.3 M | $797.1 M | 5 | 2 | 18.7% | 27.0% |
| [Kassala](Kassala/README.md) | 500,000 | 86 | $584.4 M | $114.5 M | $469.8 M | 4 | 1 | 21.7% | 21.6% |
| [Port Sudan](Port-Sudan/README.md) | 500,000 | 133 | $771.3 M | $157.9 M | $613.4 M | 4 | 1 | 18.2% | 24.4% |

## Local Basis And Regeneration

Country finance parameters use `SD` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
