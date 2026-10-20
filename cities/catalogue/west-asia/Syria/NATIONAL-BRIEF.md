# Syria National OpenSourceRail Strategy

This page contains only Syria-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$24.14 B (88.7%) of external capital** and **$31.18 B of external interest**. Capital plus saved interest totals **$55.32 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 9 |
| Represented population | 7,617,000 |
| Trainsets / vehicle modules | 1,886 / 6,305 |
| City infrastructure and fleet CAPEX | $14.41 B |
| Shared national factory | $667.5 M |
| Factory sizing basis | 1,864 modules for Aleppo, then reused nationally |
| **Total national programme** | **$15.12 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $3.08 B (20.4%) |
| Domestic / local capital | $12.04 B (79.6%) |
| Annual external capital draw | $307.7 M / yr |
| Annual local capital draw | $1.20 B / yr |
| Annual public construction commitment | $2.31 B / yr for 10 years |
| Annual post-grace debt service | $2.12 B / yr |
| Default foreign-turnkey external capital | $27.22 B |
| External capital saved | $24.14 B |
| Capital + lifetime external interest saved | $55.32 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $7.22 B | $1.08 B | $6.14 B |
| Stations | $2.98 B | $595.3 M | $2.38 B |
| Depots | $879.9 M | $220.0 M | $659.9 M |
| Rolling stock | $1.82 B | $636.9 M | $1.18 B |
| Dedicated solar plants | $454.7 M | $204.6 M | $250.1 M |
| Residual train control | $39.0 M | $19.5 M | $19.5 M |
| Charging microgrids | $99.2 M | $39.7 M | $59.5 M |
| EPC / project services | $959.4 M | $143.9 M | $815.5 M |
| Shared national trainset factory | $667.5 M | $133.5 M | $534.0 M |
| **Total** | **$15.12 B** | **$3.08 B** | **$12.04 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital | Lines | Added lines | Original circles | Current circles |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| [Damascus](Damascus/README.md) | 2,503,000 | 348 | $3.88 B | $777.1 M | $3.10 B | 9 | 3 | 38.4% | 41.2% |
| [Aleppo](Aleppo/README.md) | 1,639,000 | 466 | $4.31 B | $892.1 M | $3.42 B | 9 | 3 | 44.1% | 40.4% |
| [Homs](Homs/README.md) | 775,000 | 142 | $846.6 M | $173.4 M | $673.2 M | 4 | 1 | 29.8% | 29.9% |
| [Latakia](Latakia/README.md) | 700,000 | 168 | $998.6 M | $206.1 M | $792.5 M | 5 | 2 | 37.5% | 45.5% |
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
