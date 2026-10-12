# Guinea National OpenSourceRail Strategy

This page contains only Guinea-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$3.86 B (88.8%) of external capital** and **$4.99 B of external interest**. Capital plus saved interest totals **$8.85 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 2,010,000 |
| Trainsets / vehicle modules | 165 / 660 |
| City infrastructure and fleet CAPEX | $1.84 B |
| Shared national factory | $542.3 M |
| Factory sizing basis | 660 modules for Conakry, then reused nationally |
| **Total national programme** | **$2.42 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $488.6 M (20.2%) |
| Domestic / local capital | $1.93 B (79.8%) |
| Annual external capital draw | $48.9 M / yr |
| Annual local capital draw | $192.9 M / yr |
| Annual public construction commitment | $214.9 M / yr for 10 years |
| Annual post-grace debt service | $193.7 M / yr |
| Default foreign-turnkey external capital | $4.35 B |
| External capital saved | $3.86 B |
| Capital + lifetime external interest saved | $8.85 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $970.6 M | $145.6 M | $825.0 M |
| Stations | $359.6 M | $71.9 M | $287.7 M |
| Depots | $91.0 M | $22.7 M | $68.2 M |
| Rolling stock | $184.8 M | $64.7 M | $120.1 M |
| Dedicated solar plants | $95.9 M | $43.1 M | $52.7 M |
| Residual train control | $5.2 M | $2.6 M | $2.6 M |
| Charging microgrids | $16.6 M | $6.6 M | $9.9 M |
| EPC / project services | $151.9 M | $22.8 M | $129.1 M |
| Shared national trainset factory | $542.3 M | $108.5 M | $433.9 M |
| **Total** | **$2.42 B** | **$488.6 M** | **$1.93 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital | Lines | Added lines | Original circles | Current circles |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| [Conakry](Conakry/README.md) | 2,010,000 | 165 | $1.84 B | $374.4 M | $1.46 B | 5 | 2 | 26.0% | 36.2% |

## Local Basis And Regeneration

Country finance parameters use `GN` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
