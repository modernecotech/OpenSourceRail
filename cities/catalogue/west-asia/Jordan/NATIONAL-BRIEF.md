# Jordan National OpenSourceRail Strategy

This page contains only Jordan-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$17.39 B (88.2%) of external capital** and **$21.38 B of external interest**. Capital plus saved interest totals **$38.77 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 4 |
| Represented population | 5,557,000 |
| Trainsets / vehicle modules | 1,167 / 5,394 |
| City infrastructure and fleet CAPEX | $10.18 B |
| Shared national factory | $723.2 M |
| Factory sizing basis | 3,954 modules for Amman, then reused nationally |
| **Total national programme** | **$10.95 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $2.33 B (21.3%) |
| Domestic / local capital | $8.63 B (78.7%) |
| Annual external capital draw | $465.5 M / yr |
| Annual local capital draw | $1.73 B / yr |
| Annual public construction commitment | $967.4 M / yr for 5 years |
| Annual post-grace debt service | $695.6 M / yr |
| Default foreign-turnkey external capital | $19.72 B |
| External capital saved | $17.39 B |
| Capital + lifetime external interest saved | $38.77 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $5.50 B | $825.5 M | $4.68 B |
| Stations | $1.20 B | $239.2 M | $956.8 M |
| Depots | $569.8 M | $142.4 M | $427.3 M |
| Rolling stock | $1.54 B | $537.5 M | $998.2 M |
| Dedicated solar plants | $667.9 M | $300.6 M | $367.4 M |
| Residual train control | $29.3 M | $14.7 M | $14.7 M |
| Charging microgrids | $55.6 M | $22.3 M | $33.4 M |
| EPC / project services | $672.9 M | $100.9 M | $572.0 M |
| Shared national trainset factory | $723.2 M | $144.6 M | $578.6 M |
| **Total** | **$10.95 B** | **$2.33 B** | **$8.63 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital | Lines | Added lines | Original circles | Current circles |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| [Amman](Amman/README.md) | 4,007,000 | 659 | $7.16 B | $1.57 B | $5.60 B | 14 | 5 | 46.2% | 37.7% |
| [Zarqa](Zarqa/README.md) | 700,000 | 250 | $1.39 B | $286.2 M | $1.10 B | 5 | 2 | 33.6% | 33.1% |
| [Irbid](Irbid/README.md) | 600,000 | 174 | $985.1 M | $203.4 M | $781.7 M | 5 | 2 | 27.7% | 32.5% |
| [Aqaba](Aqaba/README.md) | 250,000 | 84 | $641.3 M | $118.5 M | $522.7 M | 4 | 1 | 58.2% | 50.4% |

## Local Basis And Regeneration

Country finance parameters use `JO` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
