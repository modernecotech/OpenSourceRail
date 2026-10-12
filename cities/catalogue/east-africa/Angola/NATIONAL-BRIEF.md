# Angola National OpenSourceRail Strategy

This page contains only Angola-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$22.03 B (88.0%) of external capital** and **$27.09 B of external interest**. Capital plus saved interest totals **$49.12 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 9 |
| Represented population | 13,135,000 |
| Trainsets / vehicle modules | 1,678 / 7,045 |
| City infrastructure and fleet CAPEX | $13.29 B |
| Shared national factory | $573.3 M |
| Factory sizing basis | 4,356 modules for Luanda, then reused nationally |
| **Total national programme** | **$13.90 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $2.99 B (21.5%) |
| Domestic / local capital | $10.91 B (78.5%) |
| Annual external capital draw | $599.0 M / yr |
| Annual local capital draw | $2.18 B / yr |
| Annual public construction commitment | $1.57 B / yr for 5 years |
| Annual post-grace debt service | $1.20 B / yr |
| Default foreign-turnkey external capital | $25.03 B |
| External capital saved | $22.03 B |
| Capital + lifetime external interest saved | $49.12 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $6.83 B | $1.02 B | $5.81 B |
| Stations | $1.78 B | $355.4 M | $1.42 B |
| Depots | $831.6 M | $207.9 M | $623.7 M |
| Rolling stock | $2.02 B | $706.9 M | $1.31 B |
| Dedicated solar plants | $905.0 M | $407.2 M | $497.7 M |
| Residual train control | $37.4 M | $18.7 M | $18.7 M |
| Charging microgrids | $80.0 M | $32.0 M | $48.0 M |
| EPC / project services | $850.4 M | $127.6 M | $722.8 M |
| Shared national trainset factory | $573.3 M | $114.7 M | $458.6 M |
| **Total** | **$13.90 B** | **$2.99 B** | **$10.91 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital | Lines | Added lines | Original circles | Current circles |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| [Luanda](Luanda/README.md) | 9,085,000 | 726 | $7.70 B | $1.75 B | $5.95 B | 14 | 5 | 40.8% | 35.8% |
| [Huambo](Huambo/README.md) | 800,000 | 194 | $1.09 B | $222.1 M | $865.3 M | 5 | 2 | 20.5% | 21.1% |
| [Lubango](Lubango/README.md) | 700,000 | 188 | $1.09 B | $223.5 M | $863.3 M | 4 | 1 | 15.3% | 26.0% |
| [Benguela](Benguela/README.md) | 600,000 | 185 | $982.9 M | $203.2 M | $779.7 M | 5 | 2 | 30.4% | 30.0% |
| [Lobito](Lobito/README.md) | 500,000 | 133 | $761.3 M | $155.5 M | $605.7 M | 4 | 1 | 18.2% | 26.6% |
| [Malanje](Malanje/README.md) | 500,000 | 46 | $280.9 M | $57.9 M | $223.0 M | 2 | 0 | 12.9% | 11.5% |
| [Uige](Uige/README.md) | 400,000 | 39 | $211.8 M | $44.3 M | $167.5 M | 1 | 0 | 6.2% | 14.0% |
| [Namibe](Namibe/README.md) | 300,000 | 103 | $730.2 M | $135.8 M | $594.4 M | 5 | 2 | 43.6% | 35.6% |
| [Soyo](Soyo/README.md) | 250,000 | 64 | $447.4 M | $84.5 M | $362.9 M | 4 | 1 | 32.8% | 24.2% |

## Local Basis And Regeneration

Country finance parameters use `AO` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
