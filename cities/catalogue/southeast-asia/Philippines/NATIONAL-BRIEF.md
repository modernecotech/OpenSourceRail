# Philippines National OpenSourceRail Strategy

This page contains only Philippines-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$9.18 B (88.3%) of external capital** and **$11.28 B of external interest**. Capital plus saved interest totals **$20.46 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 1,827,000 |
| Trainsets / vehicle modules | 593 / 2,372 |
| City infrastructure and fleet CAPEX | $5.50 B |
| Shared national factory | $257.8 M |
| Factory sizing basis | 2,372 modules for Davao, then reused nationally |
| **Total national programme** | **$5.78 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.22 B (21.1%) |
| Domestic / local capital | $4.56 B (78.9%) |
| Annual external capital draw | $244.0 M / yr |
| Annual local capital draw | $911.3 M / yr |
| Annual public construction commitment | $463.2 M / yr for 5 years |
| Annual post-grace debt service | $327.2 M / yr |
| Default foreign-turnkey external capital | $10.40 B |
| External capital saved | $9.18 B |
| Capital + lifetime external interest saved | $20.46 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $2.61 B | $391.2 M | $2.22 B |
| Stations | $1.20 B | $239.2 M | $956.6 M |
| Depots | $289.7 M | $72.4 M | $217.3 M |
| Rolling stock | $664.2 M | $232.5 M | $431.7 M |
| Dedicated solar plants | $327.5 M | $147.4 M | $180.1 M |
| Residual train control | $16.6 M | $8.3 M | $8.3 M |
| Charging microgrids | $60.2 M | $24.1 M | $36.1 M |
| EPC / project services | $356.5 M | $53.5 M | $303.0 M |
| Shared national trainset factory | $257.8 M | $51.6 M | $206.3 M |
| **Total** | **$5.78 B** | **$1.22 B** | **$4.56 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Davao](Davao/README.md) | 1,827,000 | 593 | $5.50 B | $1.17 B | $4.33 B |

## Local Basis And Regeneration

Country finance parameters use `PH` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

| City | Current lines | Added residential lines | Original station circles | Current station circles |
| --- | ---: | ---: | ---: | ---: |
| [Davao](Davao/README.md) | 15 | 9 | 42.8% | 82.8% |

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
