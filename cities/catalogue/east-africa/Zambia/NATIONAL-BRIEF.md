# Zambia National OpenSourceRail Strategy

This page contains only Zambia-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$9.15 B (87.7%) of external capital** and **$11.48 B of external interest**. Capital plus saved interest totals **$20.63 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 3,037,000 |
| Trainsets / vehicle modules | 472 / 2,832 |
| City infrastructure and fleet CAPEX | $5.25 B |
| Shared national factory | $516.9 M |
| Factory sizing basis | 2,832 modules for Lusaka, then reused nationally |
| **Total national programme** | **$5.80 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.29 B (22.2%) |
| Domestic / local capital | $4.51 B (77.8%) |
| Annual external capital draw | $183.7 M / yr |
| Annual local capital draw | $644.9 M / yr |
| Annual public construction commitment | $782.7 M / yr for 7 years |
| Annual post-grace debt service | $675.3 M / yr |
| Default foreign-turnkey external capital | $10.44 B |
| External capital saved | $9.15 B |
| Capital + lifetime external interest saved | $20.63 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $2.59 B | $388.4 M | $2.20 B |
| Stations | $724.3 M | $144.9 M | $579.4 M |
| Depots | $262.8 M | $65.7 M | $197.1 M |
| Rolling stock | $793.0 M | $277.5 M | $515.4 M |
| Dedicated solar plants | $510.1 M | $229.5 M | $280.6 M |
| Residual train control | $14.7 M | $7.3 M | $7.3 M |
| Charging microgrids | $42.6 M | $17.0 M | $25.6 M |
| EPC / project services | $346.1 M | $51.9 M | $294.2 M |
| Shared national trainset factory | $516.9 M | $103.4 M | $413.5 M |
| **Total** | **$5.80 B** | **$1.29 B** | **$4.51 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital | Lines | Added lines | Original circles | Current circles |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| [Lusaka](Lusaka/README.md) | 3,037,000 | 472 | $5.25 B | $1.18 B | $4.07 B | 12 | 4 | 39.6% | 35.3% |

## Local Basis And Regeneration

Country finance parameters use `ZM` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
