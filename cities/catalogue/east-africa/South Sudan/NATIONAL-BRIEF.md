# South Sudan National OpenSourceRail Strategy

**Uncalibrated country scenario.** Uncalibrated generic XX scenario; obtain South Sudan income, lending, FX and market-access evidence before appraisal. Numerical XX defaults are illustrative, not South Sudan country estimates or available financing.

This page contains only South Sudan-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$1.08 B (89.1%) of external capital** and **$1.33 B of external interest**. Capital plus saved interest totals **$2.41 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 300,000 |
| Trainsets / vehicle modules | 64 / 128 |
| City infrastructure and fleet CAPEX | $420.8 M |
| Shared national factory | $236.1 M |
| Factory sizing basis | 128 modules for Wau, then reused nationally |
| **Total national programme** | **$673.5 M** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $132.1 M (19.6%) |
| Domestic / local capital | $541.3 M (80.4%) |
| Annual external capital draw | $26.4 M / yr |
| Annual local capital draw | $108.3 M / yr |
| Annual public construction commitment | $57.9 M / yr for 5 years |
| Annual post-grace debt service | $41.0 M / yr |
| Default foreign-turnkey external capital | $1.21 B |
| External capital saved | $1.08 B |
| Capital + lifetime external interest saved | $2.41 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $172.7 M | $25.9 M | $146.8 M |
| Stations | $138.5 M | $27.7 M | $110.8 M |
| Depots | $43.0 M | $10.8 M | $32.3 M |
| Rolling stock | $35.8 M | $12.5 M | $23.3 M |
| Residual train control | $917 k | $459 k | $459 k |
| Charging microgrids | $2.2 M | $900 k | $1.4 M |
| EPC / project services | $44.1 M | $6.6 M | $37.4 M |
| Shared national trainset factory | $236.1 M | $47.2 M | $188.9 M |
| **Total** | **$673.5 M** | **$132.1 M** | **$541.3 M** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital | Lines | Added lines | Original circles | Current circles |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| [Wau](Wau/README.md) | 300,000 | 64 | $420.8 M | $82.4 M | $338.4 M | 3 | 0 | 9.9% | 10.6% |

## Local Basis And Regeneration

Country finance parameters use `SS` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
