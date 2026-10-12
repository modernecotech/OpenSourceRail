# Senegal National OpenSourceRail Strategy

This page contains only Senegal-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$9.12 B (87.9%) of external capital** and **$11.43 B of external interest**. Capital plus saved interest totals **$20.55 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 4,030,000 |
| Trainsets / vehicle modules | 526 / 3,156 |
| City infrastructure and fleet CAPEX | $5.40 B |
| Shared national factory | $336.1 M |
| Factory sizing basis | 3,156 modules for Dakar, then reused nationally |
| **Total national programme** | **$5.76 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.25 B (21.8%) |
| Domestic / local capital | $4.51 B (78.2%) |
| Annual external capital draw | $179.3 M / yr |
| Annual local capital draw | $644.1 M / yr |
| Annual public construction commitment | $491.9 M / yr for 7 years |
| Annual post-grace debt service | $402.6 M / yr |
| Default foreign-turnkey external capital | $10.37 B |
| External capital saved | $9.12 B |
| Capital + lifetime external interest saved | $20.55 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $2.39 B | $358.5 M | $2.03 B |
| Stations | $1.17 B | $233.4 M | $933.7 M |
| Depots | $240.3 M | $60.1 M | $180.2 M |
| Rolling stock | $883.7 M | $309.3 M | $574.4 M |
| Dedicated solar plants | $312.0 M | $140.4 M | $171.6 M |
| Residual train control | $13.4 M | $6.7 M | $6.7 M |
| Charging microgrids | $64.2 M | $25.7 M | $38.5 M |
| EPC / project services | $356.6 M | $53.5 M | $303.1 M |
| Shared national trainset factory | $336.1 M | $67.2 M | $268.9 M |
| **Total** | **$5.76 B** | **$1.25 B** | **$4.51 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital | Lines | Added lines | Original circles | Current circles |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| [Dakar](Dakar/README.md) | 4,030,000 | 526 | $5.40 B | $1.18 B | $4.22 B | 9 | 3 | 56.0% | 56.9% |

## Local Basis And Regeneration

Country finance parameters use `SN` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
