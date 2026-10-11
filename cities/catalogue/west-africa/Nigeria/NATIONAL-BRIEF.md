# Nigeria National OpenSourceRail Strategy

This page contains only Nigeria-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$78.84 B (88.1%) of external capital** and **$98.83 B of external interest**. Capital plus saved interest totals **$177.66 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 10 |
| Represented population | 19,200,000 |
| Trainsets / vehicle modules | 5,717 / 26,433 |
| City infrastructure and fleet CAPEX | $48.82 B |
| Shared national factory | $815.8 M |
| Factory sizing basis | 9,978 modules for Kano, then reused nationally |
| **Total national programme** | **$49.69 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $10.60 B (21.3%) |
| Domestic / local capital | $39.09 B (78.7%) |
| Annual external capital draw | $1.51 B / yr |
| Annual local capital draw | $5.58 B / yr |
| Annual public construction commitment | $5.82 B / yr for 7 years |
| Annual post-grace debt service | $4.91 B / yr |
| Default foreign-turnkey external capital | $89.44 B |
| External capital saved | $78.84 B |
| Capital + lifetime external interest saved | $177.66 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $22.73 B | $3.41 B | $19.32 B |
| Stations | $9.11 B | $1.82 B | $7.29 B |
| Depots | $3.79 B | $946.8 M | $2.84 B |
| Rolling stock | $7.46 B | $2.61 B | $4.85 B |
| Dedicated solar plants | $2.07 B | $933.6 M | $1.14 B |
| Residual train control | $118.4 M | $59.2 M | $59.2 M |
| Charging microgrids | $472.6 M | $189.0 M | $283.5 M |
| EPC / project services | $3.11 B | $467.2 M | $2.65 B |
| Shared national trainset factory | $815.8 M | $163.2 M | $652.6 M |
| **Total** | **$49.69 B** | **$10.60 B** | **$39.09 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Kano](Kano/README.md) | 4,200,000 | 1,663 | $15.23 B | $3.37 B | $11.86 B |
| [Ibadan](Ibadan/README.md) | 3,900,000 | 580 | $5.10 B | $1.16 B | $3.93 B |
| [Port Harcourt](Port-Harcourt/README.md) | 3,000,000 | 747 | $6.72 B | $1.40 B | $5.31 B |
| [Benin City](Benin-City/README.md) | 1,800,000 | 505 | $4.39 B | $915.2 M | $3.48 B |
| [Onitsha](Onitsha/README.md) | 1,500,000 | 764 | $6.86 B | $1.45 B | $5.41 B |
| [Maiduguri](Maiduguri/README.md) | 1,200,000 | 537 | $5.37 B | $1.06 B | $4.30 B |
| [Ilorin](Ilorin/README.md) | 1,000,000 | 285 | $1.59 B | $330.8 M | $1.26 B |
| [Aba Ng](Aba-Ng/README.md) | 900,000 | 193 | $1.11 B | $230.9 M | $881.5 M |
| [Jos](Jos/README.md) | 900,000 | 256 | $1.45 B | $296.2 M | $1.16 B |
| [Uyo](Uyo/README.md) | 800,000 | 187 | $1.01 B | $211.3 M | $796.0 M |

## Local Basis And Regeneration

Country finance parameters use `NG` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

| City | Current lines | Added residential lines | Original station circles | Current station circles |
| --- | ---: | ---: | ---: | ---: |
| [Aba Ng](Aba-Ng/README.md) | 9 | 6 | 27.2% | 56.7% |
| [Benin City](Benin-City/README.md) | 28 | 23 | 34.4% | 70.2% |
| [Ibadan](Ibadan/README.md) | 27 | 22 | 23.1% | 64.8% |
| [Ilorin](Ilorin/README.md) | 11 | 8 | 20.9% | 62.3% |
| [Jos](Jos/README.md) | 12 | 9 | 21.6% | 49.2% |
| [Kano](Kano/README.md) | 40 | 31 | 38.8% | 77.2% |
| [Maiduguri](Maiduguri/README.md) | 23 | 18 | 30.7% | 80.1% |
| [Onitsha](Onitsha/README.md) | 33 | 28 | 25.1% | 72.0% |
| [Port Harcourt](Port-Harcourt/README.md) | 30 | 25 | 23.8% | 64.6% |
| [Uyo](Uyo/README.md) | 9 | 6 | 14.7% | 36.4% |

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
