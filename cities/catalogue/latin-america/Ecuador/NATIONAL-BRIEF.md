# Ecuador National OpenSourceRail Strategy

This page contains only Ecuador-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$3.31 B (88.6%) of external capital** and **$4.07 B of external interest**. Capital plus saved interest totals **$7.37 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 817,100 |
| Trainsets / vehicle modules | 236 / 708 |
| City infrastructure and fleet CAPEX | $1.34 B |
| Shared national factory | $688.0 M |
| Factory sizing basis | 708 modules for Cuenca, then reused nationally |
| **Total national programme** | **$2.07 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $424.1 M (20.5%) |
| Domestic / local capital | $1.65 B (79.5%) |
| Annual external capital draw | $84.8 M / yr |
| Annual local capital draw | $329.7 M / yr |
| Annual public construction commitment | $210.3 M / yr for 5 years |
| Annual post-grace debt service | $155.0 M / yr |
| Default foreign-turnkey external capital | $3.73 B |
| External capital saved | $3.31 B |
| Capital + lifetime external interest saved | $7.37 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $722.8 M | $108.4 M | $614.3 M |
| Stations | $161.9 M | $32.4 M | $129.5 M |
| Depots | $92.6 M | $23.1 M | $69.4 M |
| Rolling stock | $212.4 M | $74.3 M | $138.1 M |
| Dedicated solar plants | $56.6 M | $25.5 M | $31.1 M |
| Residual train control | $3.7 M | $1.9 M | $1.9 M |
| Charging microgrids | $2.9 M | $1.1 M | $1.7 M |
| EPC / project services | $131.9 M | $19.8 M | $112.1 M |
| Shared national trainset factory | $688.0 M | $137.6 M | $550.4 M |
| **Total** | **$2.07 B** | **$424.1 M** | **$1.65 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital | Lines | Added lines | Original circles | Current circles |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| [Cuenca](Cuenca/README.md) | 817,100 | 236 | $1.34 B | $279.3 M | $1.06 B | 5 | 2 | 34.0% | 33.7% |

## Local Basis And Regeneration

Country finance parameters use `EC` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
