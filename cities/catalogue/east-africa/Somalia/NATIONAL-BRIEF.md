# Somalia National OpenSourceRail Strategy

This page contains only Somalia-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$5.05 B (88.6%) of external capital** and **$6.52 B of external interest**. Capital plus saved interest totals **$11.57 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 2,610,000 |
| Trainsets / vehicle modules | 284 / 1,136 |
| City infrastructure and fleet CAPEX | $2.75 B |
| Shared national factory | $386.4 M |
| Factory sizing basis | 1,136 modules for Mogadishu, then reused nationally |
| **Total national programme** | **$3.16 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $647.0 M (20.5%) |
| Domestic / local capital | $2.52 B (79.5%) |
| Annual external capital draw | $64.7 M / yr |
| Annual local capital draw | $251.6 M / yr |
| Annual public construction commitment | $381.4 M / yr for 10 years |
| Annual post-grace debt service | $346.3 M / yr |
| Default foreign-turnkey external capital | $5.69 B |
| External capital saved | $5.05 B |
| Capital + lifetime external interest saved | $11.57 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $1.16 B | $174.3 M | $987.4 M |
| Stations | $850.3 M | $170.1 M | $680.2 M |
| Depots | $124.7 M | $31.2 M | $93.6 M |
| Rolling stock | $318.1 M | $111.3 M | $206.8 M |
| Dedicated solar plants | $77.9 M | $35.1 M | $42.9 M |
| Residual train control | $6.7 M | $3.3 M | $3.3 M |
| Charging microgrids | $35.5 M | $14.2 M | $21.3 M |
| EPC / project services | $201.8 M | $30.3 M | $171.6 M |
| Shared national trainset factory | $386.4 M | $77.3 M | $309.1 M |
| **Total** | **$3.16 B** | **$647.0 M** | **$2.52 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital | Lines | Added lines | Original circles | Current circles |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| [Mogadishu](Mogadishu/README.md) | 2,610,000 | 284 | $2.75 B | $565.7 M | $2.18 B | 6 | 2 | 37.7% | 35.5% |

## Local Basis And Regeneration

Country finance parameters use `SO` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
