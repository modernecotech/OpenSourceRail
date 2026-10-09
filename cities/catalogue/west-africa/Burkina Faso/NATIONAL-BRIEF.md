# Burkina Faso National OpenSourceRail Strategy

This page contains only Burkina Faso-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$11.32 B (88.5%) of external capital** and **$14.63 B of external interest**. Capital plus saved interest totals **$25.95 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 2,531,000 |
| Trainsets / vehicle modules | 813 / 3,252 |
| City infrastructure and fleet CAPEX | $6.84 B |
| Shared national factory | $251.4 M |
| Factory sizing basis | 3,252 modules for Ouagadougou, then reused nationally |
| **Total national programme** | **$7.11 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.48 B (20.8%) |
| Domestic / local capital | $5.63 B (79.2%) |
| Annual external capital draw | $147.6 M / yr |
| Annual local capital draw | $563.4 M / yr |
| Annual public construction commitment | $607.3 M / yr for 10 years |
| Annual post-grace debt service | $548.9 M / yr |
| Default foreign-turnkey external capital | $12.80 B |
| External capital saved | $11.32 B |
| Capital + lifetime external interest saved | $25.95 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $3.15 B | $472.5 M | $2.68 B |
| Stations | $1.51 B | $302.6 M | $1.21 B |
| Depots | $541.6 M | $135.4 M | $406.2 M |
| Rolling stock | $910.6 M | $318.7 M | $591.9 M |
| Dedicated solar plants | $201.3 M | $90.6 M | $110.7 M |
| Residual train control | $19.4 M | $9.7 M | $9.7 M |
| Charging microgrids | $70.7 M | $28.3 M | $42.4 M |
| EPC / project services | $452.0 M | $67.8 M | $384.2 M |
| Shared national trainset factory | $251.4 M | $50.3 M | $201.1 M |
| **Total** | **$7.11 B** | **$1.48 B** | **$5.63 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Ouagadougou](Ouagadougou/README.md) | 2,531,000 | 813 | $6.84 B | $1.42 B | $5.42 B |

## Local Basis And Regeneration

Country finance parameters use `BF` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

| City | Current lines | Added residential lines | Original station circles | Current station circles |
| --- | ---: | ---: | ---: | ---: |
| [Ouagadougou](Ouagadougou/README.md) | 33 | 27 | 29.1% | 75.4% |

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
