# Angola National OpenSourceRail Strategy

This page contains only Angola-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$40.25 B (87.8%) of external capital** and **$49.48 B of external interest**. Capital plus saved interest totals **$89.73 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 9 |
| Represented population | 13,135,000 |
| Trainsets / vehicle modules | 3,336 / 14,915 |
| City infrastructure and fleet CAPEX | $24.54 B |
| Shared national factory | $869.8 M |
| Factory sizing basis | 10,404 modules for Luanda, then reused nationally |
| **Total national programme** | **$25.47 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $5.60 B (22.0%) |
| Domestic / local capital | $19.87 B (78.0%) |
| Annual external capital draw | $1.12 B / yr |
| Annual local capital draw | $3.97 B / yr |
| Annual public construction commitment | $2.87 B / yr for 5 years |
| Annual post-grace debt service | $2.19 B / yr |
| Default foreign-turnkey external capital | $45.85 B |
| External capital saved | $40.25 B |
| Capital + lifetime external interest saved | $89.73 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $10.37 B | $1.56 B | $8.81 B |
| Stations | $4.89 B | $977.2 M | $3.91 B |
| Depots | $1.99 B | $498.1 M | $1.49 B |
| Rolling stock | $4.25 B | $1.49 B | $2.77 B |
| Dedicated solar plants | $1.23 B | $551.6 M | $674.1 M |
| Residual train control | $58.1 M | $29.1 M | $29.1 M |
| Charging microgrids | $230.4 M | $92.2 M | $138.3 M |
| EPC / project services | $1.59 B | $237.9 M | $1.35 B |
| Shared national trainset factory | $869.8 M | $174.0 M | $695.8 M |
| **Total** | **$25.47 B** | **$5.60 B** | **$19.87 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Luanda](Luanda/README.md) | 9,085,000 | 1,734 | $15.56 B | $3.59 B | $11.97 B |
| [Huambo](Huambo/README.md) | 800,000 | 308 | $1.68 B | $344.5 M | $1.33 B |
| [Lubango](Lubango/README.md) | 700,000 | 306 | $1.70 B | $351.9 M | $1.35 B |
| [Benguela](Benguela/README.md) | 600,000 | 333 | $1.75 B | $361.8 M | $1.39 B |
| [Lobito](Lobito/README.md) | 500,000 | 222 | $1.15 B | $240.9 M | $911.4 M |
| [Malanje](Malanje/README.md) | 500,000 | 97 | $582.1 M | $119.2 M | $462.9 M |
| [Uige](Uige/README.md) | 400,000 | 41 | $238.2 M | $49.1 M | $189.1 M |
| [Namibe](Namibe/README.md) | 300,000 | 180 | $1.16 B | $222.6 M | $933.8 M |
| [Soyo](Soyo/README.md) | 250,000 | 115 | $722.1 M | $141.4 M | $580.6 M |

## Local Basis And Regeneration

Country finance parameters use `AO` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

| City | Current lines | Added residential lines | Original station circles | Current station circles |
| --- | ---: | ---: | ---: | ---: |
| [Benguela](Benguela/README.md) | 14 | 11 | 30.4% | 68.6% |
| [Huambo](Huambo/README.md) | 13 | 10 | 20.5% | 51.0% |
| [Lobito](Lobito/README.md) | 8 | 5 | 18.2% | 63.6% |
| [Luanda](Luanda/README.md) | 45 | 36 | 40.8% | 75.6% |
| [Lubango](Lubango/README.md) | 10 | 7 | 15.3% | 51.7% |
| [Malanje](Malanje/README.md) | 5 | 3 | 12.9% | 26.1% |
| [Namibe](Namibe/README.md) | 11 | 8 | 43.6% | 77.2% |
| [Soyo](Soyo/README.md) | 6 | 3 | 32.8% | 51.2% |
| [Uige](Uige/README.md) | 2 | 1 | 6.2% | 16.3% |

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
