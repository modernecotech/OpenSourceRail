# Zambia National OpenSourceRail Strategy

This page contains only Zambia-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$14.50 B (87.3%) of external capital** and **$18.18 B of external interest**. Capital plus saved interest totals **$32.69 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 3,037,000 |
| Trainsets / vehicle modules | 962 / 5,772 |
| City infrastructure and fleet CAPEX | $8.86 B |
| Shared national factory | $346.3 M |
| Factory sizing basis | 5,772 modules for Lusaka, then reused nationally |
| **Total national programme** | **$9.23 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $2.10 B (22.8%) |
| Domestic / local capital | $7.12 B (77.2%) |
| Annual external capital draw | $300.3 M / yr |
| Annual local capital draw | $1.02 B / yr |
| Annual public construction commitment | $1.24 B / yr for 7 years |
| Annual post-grace debt service | $1.07 B / yr |
| Default foreign-turnkey external capital | $16.61 B |
| External capital saved | $14.50 B |
| Capital + lifetime external interest saved | $32.69 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $3.56 B | $533.5 M | $3.02 B |
| Stations | $1.75 B | $349.6 M | $1.40 B |
| Depots | $624.3 M | $156.1 M | $468.2 M |
| Rolling stock | $1.62 B | $565.7 M | $1.05 B |
| Dedicated solar plants | $646.8 M | $291.1 M | $355.7 M |
| Residual train control | $20.3 M | $10.1 M | $10.1 M |
| Charging microgrids | $105.8 M | $42.3 M | $63.5 M |
| EPC / project services | $561.2 M | $84.2 M | $477.1 M |
| Shared national trainset factory | $346.3 M | $69.3 M | $277.1 M |
| **Total** | **$9.23 B** | **$2.10 B** | **$7.12 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Lusaka](Lusaka/README.md) | 3,037,000 | 962 | $8.86 B | $2.03 B | $6.83 B |

## Local Basis And Regeneration

Country finance parameters use `ZM` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

| City | Current lines | Added residential lines | Original station circles | Current station circles |
| --- | ---: | ---: | ---: | ---: |
| [Lusaka](Lusaka/README.md) | 32 | 24 | 39.6% | 78.8% |

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
