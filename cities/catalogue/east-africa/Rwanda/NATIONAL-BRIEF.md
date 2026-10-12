# Rwanda National OpenSourceRail Strategy

This page contains only Rwanda-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$8.76 B (89.1%) of external capital** and **$10.98 B of external interest**. Capital plus saved interest totals **$19.73 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 3 |
| Represented population | 1,708,000 |
| Trainsets / vehicle modules | 460 / 1,434 |
| City infrastructure and fleet CAPEX | $4.61 B |
| Shared national factory | $794.6 M |
| Factory sizing basis | 1,028 modules for Kigali, then reused nationally |
| **Total national programme** | **$5.46 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.08 B (19.7%) |
| Domestic / local capital | $4.39 B (80.3%) |
| Annual external capital draw | $153.6 M / yr |
| Annual local capital draw | $626.7 M / yr |
| Annual public construction commitment | $472.1 M / yr for 7 years |
| Annual post-grace debt service | $383.2 M / yr |
| Default foreign-turnkey external capital | $9.83 B |
| External capital saved | $8.76 B |
| Capital + lifetime external interest saved | $19.73 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $2.79 B | $418.4 M | $2.37 B |
| Stations | $587.9 M | $117.6 M | $470.3 M |
| Depots | $284.8 M | $71.2 M | $213.6 M |
| Rolling stock | $401.5 M | $140.5 M | $261.0 M |
| Dedicated solar plants | $224.4 M | $101.0 M | $123.4 M |
| Residual train control | $14.7 M | $7.3 M | $7.3 M |
| Charging microgrids | $22.9 M | $9.1 M | $13.7 M |
| EPC / project services | $342.7 M | $51.4 M | $291.3 M |
| Shared national trainset factory | $794.6 M | $158.9 M | $635.7 M |
| **Total** | **$5.46 B** | **$1.08 B** | **$4.39 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital | Lines | Added lines | Original circles | Current circles |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| [Kigali](Kigali/README.md) | 1,208,000 | 257 | $3.15 B | $631.9 M | $2.52 B | 9 | 3 | 37.0% | 41.1% |
| [Huye](Huye/README.md) | 250,000 | 108 | $804.4 M | $150.9 M | $653.6 M | 5 | 2 | 26.0% | 27.5% |
| [Rubavu](Rubavu/README.md) | 250,000 | 95 | $660.1 M | $125.4 M | $534.7 M | 4 | 1 | 34.9% | 32.6% |

## Local Basis And Regeneration

Country finance parameters use `RW` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
