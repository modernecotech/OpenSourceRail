# Syria National OpenSourceRail Strategy

This page contains only Syria-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$23.73 B (88.7%) of external capital** and **$30.65 B of external interest**. Capital plus saved interest totals **$54.39 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 9 |
| Represented population | 7,617,000 |
| Trainsets / vehicle modules | 1,853 / 6,206 |
| City infrastructure and fleet CAPEX | $14.15 B |
| Shared national factory | $667.5 M |
| Factory sizing basis | 1,864 modules for Aleppo, then reused nationally |
| **Total national programme** | **$14.86 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $3.02 B (20.3%) |
| Domestic / local capital | $11.84 B (79.7%) |
| Annual external capital draw | $302.4 M / yr |
| Annual local capital draw | $1.18 B / yr |
| Annual public construction commitment | $2.27 B / yr for 10 years |
| Annual post-grace debt service | $2.09 B / yr |
| Default foreign-turnkey external capital | $26.76 B |
| External capital saved | $23.73 B |
| Capital + lifetime external interest saved | $54.39 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $7.15 B | $1.07 B | $6.08 B |
| Stations | $2.85 B | $569.8 M | $2.28 B |
| Depots | $874.6 M | $218.7 M | $656.0 M |
| Rolling stock | $1.79 B | $626.5 M | $1.16 B |
| Dedicated solar plants | $451.3 M | $203.1 M | $248.2 M |
| Residual train control | $38.6 M | $19.3 M | $19.3 M |
| Charging microgrids | $97.7 M | $39.1 M | $58.6 M |
| EPC / project services | $942.9 M | $141.4 M | $801.5 M |
| Shared national trainset factory | $667.5 M | $133.5 M | $534.0 M |
| **Total** | **$14.86 B** | **$3.02 B** | **$11.84 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital | Lines | Added lines | Original circles | Current circles |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| [Damascus](Damascus/README.md) | 2,503,000 | 348 | $3.88 B | $777.1 M | $3.10 B | 9 | 3 | 38.4% | 41.2% |
| [Aleppo](Aleppo/README.md) | 1,639,000 | 466 | $4.31 B | $892.1 M | $3.42 B | 9 | 3 | 44.1% | 40.4% |
| [Homs](Homs/README.md) | 775,000 | 142 | $846.6 M | $173.4 M | $673.2 M | 4 | 1 | 29.8% | 29.9% |
| [Latakia](Latakia/README.md) | 700,000 | 135 | $742.9 M | $153.4 M | $589.5 M | 5 | 2 | 37.5% | 41.0% |
| [Hama](Hama/README.md) | 600,000 | 229 | $1.26 B | $262.2 M | $1.00 B | 5 | 2 | 33.5% | 43.6% |
| [Deir Ez Zor](Deir-Ez-Zor/README.md) | 500,000 | 210 | $1.12 B | $232.2 M | $883.2 M | 5 | 2 | 43.1% | 45.2% |
| [Raqqa](Raqqa/README.md) | 350,000 | 156 | $834.9 M | $173.8 M | $661.2 M | 4 | 1 | 42.1% | 45.2% |
| [Idlib](Idlib/README.md) | 300,000 | 87 | $617.1 M | $116.2 M | $500.8 M | 4 | 1 | 55.7% | 60.4% |
| [Tartus](Tartus/README.md) | 250,000 | 80 | $542.4 M | $103.3 M | $439.1 M | 4 | 1 | 43.7% | 49.0% |

## Local Basis And Regeneration

Country finance parameters use `SY` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
