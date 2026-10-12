# Nepal National OpenSourceRail Strategy

This page contains only Nepal-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$12.71 B (88.7%) of external capital** and **$15.93 B of external interest**. Capital plus saved interest totals **$28.63 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 3 |
| Represented population | 2,342,000 |
| Trainsets / vehicle modules | 811 / 2,809 |
| City infrastructure and fleet CAPEX | $7.06 B |
| Shared national factory | $836.7 M |
| Factory sizing basis | 1,788 modules for Kathmandu, then reused nationally |
| **Total national programme** | **$7.96 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.62 B (20.4%) |
| Domestic / local capital | $6.34 B (79.6%) |
| Annual external capital draw | $231.6 M / yr |
| Annual local capital draw | $905.4 M / yr |
| Annual public construction commitment | $634.3 M / yr for 7 years |
| Annual post-grace debt service | $514.0 M / yr |
| Default foreign-turnkey external capital | $14.33 B |
| External capital saved | $12.71 B |
| Capital + lifetime external interest saved | $28.63 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $3.71 B | $557.1 M | $3.16 B |
| Stations | $1.35 B | $269.2 M | $1.08 B |
| Depots | $347.0 M | $86.7 M | $260.2 M |
| Rolling stock | $804.1 M | $281.4 M | $522.7 M |
| Dedicated solar plants | $347.6 M | $156.4 M | $191.2 M |
| Residual train control | $18.2 M | $9.1 M | $9.1 M |
| Charging microgrids | $47.6 M | $19.1 M | $28.6 M |
| EPC / project services | $498.0 M | $74.7 M | $423.3 M |
| Shared national trainset factory | $836.7 M | $167.3 M | $669.3 M |
| **Total** | **$7.96 B** | **$1.62 B** | **$6.34 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital | Lines | Added lines | Original circles | Current circles |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| [Kathmandu](Kathmandu/README.md) | 1,442,000 | 447 | $4.74 B | $984.4 M | $3.75 B | 9 | 3 | 53.0% | 46.5% |
| [Pokhara](Pokhara/README.md) | 600,000 | 293 | $1.62 B | $335.5 M | $1.29 B | 5 | 2 | 43.2% | 45.5% |
| [Biratnagar](Biratnagar/README.md) | 300,000 | 71 | $704.1 M | $125.1 M | $579.1 M | 4 | 1 | 26.2% | 32.0% |

## Local Basis And Regeneration

Country finance parameters use `NP` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
