# South Sudan National OpenSourceRail Strategy

**Uncalibrated country scenario.** Uncalibrated generic XX scenario; obtain South Sudan income, lending, FX and market-access evidence before appraisal. Numerical XX defaults are illustrative, not South Sudan country estimates or available financing.

This page contains only South Sudan-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$826.7 M (89.2%) of external capital** and **$1.02 B of external interest**. Capital plus saved interest totals **$1.84 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 300,000 |
| Trainsets / vehicle modules | 45 / 90 |
| City infrastructure and fleet CAPEX | $310.3 M |
| Shared national factory | $191.0 M |
| Factory sizing basis | 90 modules for Wau, then reused nationally |
| **Total national programme** | **$514.6 M** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $99.6 M (19.4%) |
| Domestic / local capital | $415.0 M (80.6%) |
| Annual external capital draw | $19.9 M / yr |
| Annual local capital draw | $83.0 M / yr |
| Annual public construction commitment | $44.3 M / yr for 5 years |
| Annual post-grace debt service | $31.3 M / yr |
| Default foreign-turnkey external capital | $926.4 M |
| External capital saved | $826.7 M |
| Capital + lifetime external interest saved | $1.84 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $158.4 M | $23.8 M | $134.6 M |
| Stations | $64.5 M | $12.9 M | $51.6 M |
| Depots | $39.7 M | $9.9 M | $29.8 M |
| Rolling stock | $25.2 M | $8.8 M | $16.4 M |
| Residual train control | $841 k | $420 k | $420 k |
| Charging microgrids | $1.4 M | $540 k | $810 k |
| EPC / project services | $33.7 M | $5.1 M | $28.6 M |
| Shared national trainset factory | $191.0 M | $38.2 M | $152.8 M |
| **Total** | **$514.6 M** | **$99.6 M** | **$415.0 M** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital | Lines | Added lines | Original circles | Current circles |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| [Wau](Wau/README.md) | 300,000 | 45 | $310.3 M | $59.4 M | $250.9 M | 3 | 0 | 9.9% | 9.9% |

## Local Basis And Regeneration

Country finance parameters use `SS` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
