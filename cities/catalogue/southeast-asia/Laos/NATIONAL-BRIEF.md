# Laos National OpenSourceRail Strategy

This page contains only Laos-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$3.66 B (88.5%) of external capital** and **$4.59 B of external interest**. Capital plus saved interest totals **$8.26 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 948,000 |
| Trainsets / vehicle modules | 270 / 810 |
| City infrastructure and fleet CAPEX | $1.47 B |
| Shared national factory | $770.6 M |
| Factory sizing basis | 810 modules for Vientiane, then reused nationally |
| **Total national programme** | **$2.30 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $474.1 M (20.6%) |
| Domestic / local capital | $1.82 B (79.4%) |
| Annual external capital draw | $67.7 M / yr |
| Annual local capital draw | $260.7 M / yr |
| Annual public construction commitment | $226.8 M / yr for 7 years |
| Annual post-grace debt service | $187.1 M / yr |
| Default foreign-turnkey external capital | $4.14 B |
| External capital saved | $3.66 B |
| Capital + lifetime external interest saved | $8.26 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $785.1 M | $117.8 M | $667.4 M |
| Stations | $178.7 M | $35.7 M | $143.0 M |
| Depots | $98.0 M | $24.5 M | $73.5 M |
| Rolling stock | $243.0 M | $85.0 M | $157.9 M |
| Dedicated solar plants | $70.2 M | $31.6 M | $38.6 M |
| Residual train control | $4.4 M | $2.2 M | $2.2 M |
| Charging microgrids | $3.4 M | $1.3 M | $2.0 M |
| EPC / project services | $145.8 M | $21.9 M | $123.9 M |
| Shared national trainset factory | $770.6 M | $154.1 M | $616.5 M |
| **Total** | **$2.30 B** | **$474.1 M** | **$1.82 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital | Lines | Added lines | Original circles | Current circles |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| [Vientiane](Vientiane/README.md) | 948,000 | 270 | $1.47 B | $311.9 M | $1.16 B | 5 | 2 | 26.4% | 35.3% |

## Local Basis And Regeneration

Country finance parameters use `LA` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
