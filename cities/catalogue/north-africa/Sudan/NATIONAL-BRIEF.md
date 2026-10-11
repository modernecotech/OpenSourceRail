# Sudan National OpenSourceRail Strategy

This page contains only Sudan-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$48.94 B (88.0%) of external capital** and **$63.22 B of external interest**. Capital plus saved interest totals **$112.16 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 6 |
| Represented population | 10,729,000 |
| Trainsets / vehicle modules | 3,662 / 17,269 |
| City infrastructure and fleet CAPEX | $30.04 B |
| Shared national factory | $796.5 M |
| Factory sizing basis | 10,458 modules for Khartoum, then reused nationally |
| **Total national programme** | **$30.89 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $6.66 B (21.6%) |
| Domestic / local capital | $24.23 B (78.4%) |
| Annual external capital draw | $666.1 M / yr |
| Annual local capital draw | $2.42 B / yr |
| Annual public construction commitment | $3.69 B / yr for 10 years |
| Annual post-grace debt service | $3.36 B / yr |
| Default foreign-turnkey external capital | $55.60 B |
| External capital saved | $48.94 B |
| Capital + lifetime external interest saved | $112.16 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $13.13 B | $1.97 B | $11.16 B |
| Stations | $6.26 B | $1.25 B | $5.01 B |
| Depots | $2.26 B | $564.5 M | $1.69 B |
| Rolling stock | $4.89 B | $1.71 B | $3.18 B |
| Dedicated solar plants | $1.23 B | $552.1 M | $674.8 M |
| Residual train control | $73.3 M | $36.7 M | $36.7 M |
| Charging microgrids | $310.4 M | $124.2 M | $186.2 M |
| EPC / project services | $1.94 B | $291.1 M | $1.65 B |
| Shared national trainset factory | $796.5 M | $159.3 M | $637.2 M |
| **Total** | **$30.89 B** | **$6.66 B** | **$24.23 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Khartoum](Khartoum/README.md) | 5,829,000 | 1,743 | $15.78 B | $3.55 B | $12.23 B |
| [Omdurman](Omdurman/README.md) | 2,800,000 | 1,054 | $9.12 B | $1.90 B | $7.22 B |
| [Nyala](Nyala/README.md) | 600,000 | 276 | $1.68 B | $336.6 M | $1.34 B |
| [El Obeid](El-Obeid/README.md) | 500,000 | 262 | $1.50 B | $307.9 M | $1.19 B |
| [Kassala](Kassala/README.md) | 500,000 | 152 | $1.02 B | $201.0 M | $817.0 M |
| [Port Sudan](Port-Sudan/README.md) | 500,000 | 175 | $949.7 M | $195.2 M | $754.5 M |

## Local Basis And Regeneration

Country finance parameters use `SD` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

| City | Current lines | Added residential lines | Original station circles | Current station circles |
| --- | ---: | ---: | ---: | ---: |
| [El Obeid](El-Obeid/README.md) | 10 | 7 | 18.7% | 42.5% |
| [Kassala](Kassala/README.md) | 8 | 5 | 21.7% | 46.9% |
| [Khartoum](Khartoum/README.md) | 50 | 41 | 22.4% | 59.3% |
| [Nyala](Nyala/README.md) | 12 | 9 | 18.4% | 41.6% |
| [Omdurman](Omdurman/README.md) | 40 | 34 | 24.5% | 65.9% |
| [Port Sudan](Port-Sudan/README.md) | 7 | 4 | 18.2% | 43.4% |

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
