# Madagascar National OpenSourceRail Strategy

This page contains only Madagascar-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$12.86 B (87.7%) of external capital** and **$16.61 B of external interest**. Capital plus saved interest totals **$29.47 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 3,058,000 |
| Trainsets / vehicle modules | 752 / 4,512 |
| City infrastructure and fleet CAPEX | $7.77 B |
| Shared national factory | $354.4 M |
| Factory sizing basis | 4,512 modules for Antananarivo, then reused nationally |
| **Total national programme** | **$8.15 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.81 B (22.2%) |
| Domestic / local capital | $6.34 B (77.8%) |
| Annual external capital draw | $181.2 M / yr |
| Annual local capital draw | $634.0 M / yr |
| Annual public construction commitment | $766.2 M / yr for 10 years |
| Annual post-grace debt service | $694.6 M / yr |
| Default foreign-turnkey external capital | $14.67 B |
| External capital saved | $12.86 B |
| Capital + lifetime external interest saved | $29.47 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $3.57 B | $536.0 M | $3.04 B |
| Stations | $1.39 B | $277.8 M | $1.11 B |
| Depots | $358.1 M | $89.5 M | $268.6 M |
| Rolling stock | $1.26 B | $442.2 M | $821.2 M |
| Dedicated solar plants | $627.3 M | $282.3 M | $345.0 M |
| Residual train control | $17.8 M | $8.9 M | $8.9 M |
| Charging microgrids | $76.0 M | $30.4 M | $45.6 M |
| EPC / project services | $492.2 M | $73.8 M | $418.4 M |
| Shared national trainset factory | $354.4 M | $70.9 M | $283.5 M |
| **Total** | **$8.15 B** | **$1.81 B** | **$6.34 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital | Lines | Added lines | Original circles | Current circles |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| [Antananarivo](Antananarivo/README.md) | 3,058,000 | 752 | $7.77 B | $1.74 B | $6.04 B | 14 | 5 | 35.7% | 36.2% |

## Local Basis And Regeneration

Country finance parameters use `MG` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
