# Myanmar National OpenSourceRail Strategy

This page contains only Myanmar-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$33.56 B (87.8%) of external capital** and **$43.36 B of external interest**. Capital plus saved interest totals **$76.92 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 2 |
| Represented population | 6,926,000 |
| Trainsets / vehicle modules | 2,186 / 11,892 |
| City infrastructure and fleet CAPEX | $20.64 B |
| Shared national factory | $566.6 M |
| Factory sizing basis | 9,444 modules for Yangon, then reused nationally |
| **Total national programme** | **$21.25 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $4.68 B (22.0%) |
| Domestic / local capital | $16.56 B (78.0%) |
| Annual external capital draw | $468.3 M / yr |
| Annual local capital draw | $1.66 B / yr |
| Annual public construction commitment | $2.26 B / yr for 10 years |
| Annual post-grace debt service | $2.06 B / yr |
| Default foreign-turnkey external capital | $38.25 B |
| External capital saved | $33.56 B |
| Capital + lifetime external interest saved | $76.92 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $9.10 B | $1.36 B | $7.73 B |
| Stations | $4.20 B | $839.3 M | $3.36 B |
| Depots | $1.13 B | $282.4 M | $847.1 M |
| Rolling stock | $3.33 B | $1.17 B | $2.16 B |
| Dedicated solar plants | $1.35 B | $606.1 M | $740.8 M |
| Residual train control | $49.5 M | $24.8 M | $24.8 M |
| Charging microgrids | $229.6 M | $91.8 M | $137.8 M |
| EPC / project services | $1.30 B | $195.3 M | $1.11 B |
| Shared national trainset factory | $566.6 M | $113.3 M | $453.3 M |
| **Total** | **$21.25 B** | **$4.68 B** | **$16.56 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Yangon](Yangon/README.md) | 5,200,000 | 1,574 | $14.70 B | $3.36 B | $11.33 B |
| [Mandalay](Mandalay/README.md) | 1,726,000 | 612 | $5.94 B | $1.20 B | $4.74 B |

## Local Basis And Regeneration

Country finance parameters use `MM` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

| City | Current lines | Added residential lines | Original station circles | Current station circles |
| --- | ---: | ---: | ---: | ---: |
| [Mandalay](Mandalay/README.md) | 20 | 14 | 40.5% | 81.2% |
| [Yangon](Yangon/README.md) | 32 | 23 | 46.6% | 83.7% |

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
