# Rwanda National OpenSourceRail Strategy

This page contains only Rwanda-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$14.23 B (88.6%) of external capital** and **$17.83 B of external interest**. Capital plus saved interest totals **$32.06 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 3 |
| Represented population | 1,708,000 |
| Trainsets / vehicle modules | 1,057 / 3,446 |
| City infrastructure and fleet CAPEX | $8.29 B |
| Shared national factory | $587.3 M |
| Factory sizing basis | 2,664 modules for Kigali, then reused nationally |
| **Total national programme** | **$8.92 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.83 B (20.5%) |
| Domestic / local capital | $7.09 B (79.5%) |
| Annual external capital draw | $261.7 M / yr |
| Annual local capital draw | $1.01 B / yr |
| Annual public construction commitment | $767.0 M / yr for 7 years |
| Annual post-grace debt service | $624.7 M / yr |
| Default foreign-turnkey external capital | $16.06 B |
| External capital saved | $14.23 B |
| Capital + lifetime external interest saved | $32.06 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $3.77 B | $565.8 M | $3.21 B |
| Stations | $1.92 B | $383.2 M | $1.53 B |
| Depots | $779.0 M | $194.8 M | $584.3 M |
| Rolling stock | $964.9 M | $337.7 M | $627.2 M |
| Dedicated solar plants | $240.7 M | $108.3 M | $132.4 M |
| Residual train control | $22.6 M | $11.3 M | $11.3 M |
| Charging microgrids | $70.7 M | $28.3 M | $42.4 M |
| EPC / project services | $567.9 M | $85.2 M | $482.7 M |
| Shared national trainset factory | $587.3 M | $117.5 M | $469.8 M |
| **Total** | **$8.92 B** | **$1.83 B** | **$7.09 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Kigali](Kigali/README.md) | 1,208,000 | 666 | $5.86 B | $1.24 B | $4.63 B |
| [Huye](Huye/README.md) | 250,000 | 204 | $1.29 B | $251.4 M | $1.04 B |
| [Rubavu](Rubavu/README.md) | 250,000 | 187 | $1.14 B | $220.3 M | $915.6 M |

## Local Basis And Regeneration

Country finance parameters use `RW` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

| City | Current lines | Added residential lines | Original station circles | Current station circles |
| --- | ---: | ---: | ---: | ---: |
| [Huye](Huye/README.md) | 12 | 9 | 26.0% | 60.8% |
| [Kigali](Kigali/README.md) | 30 | 24 | 37.0% | 77.5% |
| [Rubavu](Rubavu/README.md) | 10 | 7 | 34.9% | 78.7% |

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
