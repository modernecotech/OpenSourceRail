# Niger National OpenSourceRail Strategy

This page contains only Niger-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$9.52 B (88.6%) of external capital** and **$12.30 B of external interest**. Capital plus saved interest totals **$21.82 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 1,407,635 |
| Trainsets / vehicle modules | 665 / 2,660 |
| City infrastructure and fleet CAPEX | $5.70 B |
| Shared national factory | $255.8 M |
| Factory sizing basis | 2,660 modules for Niamey, then reused nationally |
| **Total national programme** | **$5.97 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.23 B (20.5%) |
| Domestic / local capital | $4.74 B (79.5%) |
| Annual external capital draw | $122.6 M / yr |
| Annual local capital draw | $474.4 M / yr |
| Annual public construction commitment | $491.7 M / yr for 10 years |
| Annual post-grace debt service | $444.7 M / yr |
| Default foreign-turnkey external capital | $10.75 B |
| External capital saved | $9.52 B |
| Capital + lifetime external interest saved | $21.82 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $2.54 B | $381.1 M | $2.16 B |
| Stations | $1.36 B | $272.0 M | $1.09 B |
| Depots | $511.0 M | $127.8 M | $383.3 M |
| Rolling stock | $744.8 M | $260.7 M | $484.1 M |
| Dedicated solar plants | $97.7 M | $43.9 M | $53.7 M |
| Residual train control | $14.3 M | $7.2 M | $7.2 M |
| Charging microgrids | $62.5 M | $25.0 M | $37.5 M |
| EPC / project services | $384.2 M | $57.6 M | $326.6 M |
| Shared national trainset factory | $255.8 M | $51.2 M | $204.7 M |
| **Total** | **$5.97 B** | **$1.23 B** | **$4.74 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Niamey](Niamey/README.md) | 1,407,635 | 665 | $5.70 B | $1.17 B | $4.52 B |

## Local Basis And Regeneration

Country finance parameters use `NE` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

| City | Current lines | Added residential lines | Original station circles | Current station circles |
| --- | ---: | ---: | ---: | ---: |
| [Niamey](Niamey/README.md) | 33 | 27 | 35.0% | 78.4% |

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
