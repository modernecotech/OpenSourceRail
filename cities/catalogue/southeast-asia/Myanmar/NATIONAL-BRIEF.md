# Myanmar National OpenSourceRail Strategy

This page contains only Myanmar-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$23.75 B (88.0%) of external capital** and **$30.68 B of external interest**. Capital plus saved interest totals **$54.43 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 2 |
| Represented population | 6,926,000 |
| Trainsets / vehicle modules | 1,275 / 7,012 |
| City infrastructure and fleet CAPEX | $14.37 B |
| Shared national factory | $579.8 M |
| Factory sizing basis | 5,736 modules for Yangon, then reused nationally |
| **Total national programme** | **$14.99 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $3.24 B (21.6%) |
| Domestic / local capital | $11.75 B (78.4%) |
| Annual external capital draw | $324.1 M / yr |
| Annual local capital draw | $1.18 B / yr |
| Annual public construction commitment | $1.60 B / yr for 10 years |
| Annual post-grace debt service | $1.45 B / yr |
| Default foreign-turnkey external capital | $26.99 B |
| External capital saved | $23.75 B |
| Capital + lifetime external interest saved | $54.43 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $7.39 B | $1.11 B | $6.28 B |
| Stations | $2.24 B | $447.3 M | $1.79 B |
| Depots | $577.7 M | $144.4 M | $433.3 M |
| Rolling stock | $1.96 B | $687.2 M | $1.28 B |
| Dedicated solar plants | $1.19 B | $536.4 M | $655.6 M |
| Residual train control | $39.8 M | $19.9 M | $19.9 M |
| Charging microgrids | $117.7 M | $47.1 M | $70.6 M |
| EPC / project services | $903.0 M | $135.4 M | $767.5 M |
| Shared national trainset factory | $579.8 M | $116.0 M | $463.8 M |
| **Total** | **$14.99 B** | **$3.24 B** | **$11.75 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital | Lines | Added lines | Original circles | Current circles |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| [Yangon](Yangon/README.md) | 5,200,000 | 956 | $10.53 B | $2.37 B | $8.16 B | 14 | 5 | 46.6% | 44.8% |
| [Mandalay](Mandalay/README.md) | 1,726,000 | 319 | $3.85 B | $753.1 M | $3.09 B | 9 | 3 | 40.5% | 42.1% |

## Local Basis And Regeneration

Country finance parameters use `MM` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
