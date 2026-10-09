# South Sudan National OpenSourceRail Strategy

**Uncalibrated country scenario.** Uncalibrated generic XX scenario; obtain South Sudan income, lending, FX and market-access evidence before appraisal. Numerical XX defaults are illustrative, not South Sudan country estimates or available financing.

This page contains only South Sudan-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$760.6 M (89.2%) of external capital** and **$935.2 M of external interest**. Capital plus saved interest totals **$1.70 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 300,000 |
| Trainsets / vehicle modules | 43 / 86 |
| City infrastructure and fleet CAPEX | $275.1 M |
| Shared national factory | $185.9 M |
| Factory sizing basis | 86 modules for Wau, then reused nationally |
| **Total national programme** | **$474.0 M** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $92.5 M (19.5%) |
| Domestic / local capital | $381.5 M (80.5%) |
| Annual external capital draw | $18.5 M / yr |
| Annual local capital draw | $76.3 M / yr |
| Annual public construction commitment | $40.8 M / yr for 5 years |
| Annual post-grace debt service | $28.9 M / yr |
| Default foreign-turnkey external capital | $853.1 M |
| External capital saved | $760.6 M |
| Capital + lifetime external interest saved | $1.70 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $137.1 M | $20.6 M | $116.5 M |
| Stations | $53.6 M | $10.7 M | $42.9 M |
| Depots | $40.3 M | $10.1 M | $30.2 M |
| Rolling stock | $24.1 M | $8.4 M | $15.7 M |
| Residual train control | $763 k | $382 k | $382 k |
| Charging microgrids | $1.2 M | $500 k | $750 k |
| EPC / project services | $31.0 M | $4.7 M | $26.4 M |
| Shared national trainset factory | $185.9 M | $37.2 M | $148.7 M |
| **Total** | **$474.0 M** | **$92.5 M** | **$381.5 M** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Wau](Wau/README.md) | 300,000 | 43 | $275.1 M | $53.4 M | $221.7 M |

## Local Basis And Regeneration

Country finance parameters use `SS` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

| City | Current lines | Added residential lines | Original station circles | Current station circles |
| --- | ---: | ---: | ---: | ---: |
| [Wau](Wau/README.md) | 3 | 0 | 9.9% | 11.2% |

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
