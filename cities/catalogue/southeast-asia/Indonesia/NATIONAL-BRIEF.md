# Indonesia National OpenSourceRail Strategy

This page contains only Indonesia-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$19.46 B (88.0%) of external capital** and **$23.92 B of external interest**. Capital plus saved interest totals **$43.38 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 2 |
| Represented population | 5,624,000 |
| Trainsets / vehicle modules | 1,139 / 5,820 |
| City infrastructure and fleet CAPEX | $11.91 B |
| Shared national factory | $347.0 M |
| Factory sizing basis | 3,792 modules for Surabaya, then reused nationally |
| **Total national programme** | **$12.28 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $2.65 B (21.6%) |
| Domestic / local capital | $9.63 B (78.4%) |
| Annual external capital draw | $530.5 M / yr |
| Annual local capital draw | $1.93 B / yr |
| Annual public construction commitment | $1.02 B / yr for 5 years |
| Annual post-grace debt service | $727.7 M / yr |
| Default foreign-turnkey external capital | $22.11 B |
| External capital saved | $19.46 B |
| Capital + lifetime external interest saved | $43.38 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $5.47 B | $820.8 M | $4.65 B |
| Stations | $2.67 B | $533.6 M | $2.13 B |
| Depots | $437.7 M | $109.4 M | $328.2 M |
| Rolling stock | $1.63 B | $570.4 M | $1.06 B |
| Dedicated solar plants | $826.4 M | $371.9 M | $454.5 M |
| Residual train control | $28.3 M | $14.2 M | $14.2 M |
| Charging microgrids | $126.0 M | $50.4 M | $75.6 M |
| EPC / project services | $749.6 M | $112.4 M | $637.1 M |
| Shared national trainset factory | $347.0 M | $69.4 M | $277.6 M |
| **Total** | **$12.28 B** | **$2.65 B** | **$9.63 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital | Lines | Added lines | Original circles | Current circles |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| [Surabaya](Surabaya/README.md) | 3,009,000 | 632 | $6.73 B | $1.51 B | $5.23 B | 9 | 0 | Unavailable | Unavailable |
| [Bandung](Bandung/README.md) | 2,615,000 | 507 | $5.18 B | $1.07 B | $4.11 B | 6 | 0 | Unavailable | Unavailable |

## Local Basis And Regeneration

Country finance parameters use `ID` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
