# Angola National OpenSourceRail Strategy

This page contains only Angola-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$25.69 B (88.0%) of external capital** and **$31.58 B of external interest**. Capital plus saved interest totals **$57.27 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 9 |
| Represented population | 13,135,000 |
| Trainsets / vehicle modules | 1,992 / 8,533 |
| City infrastructure and fleet CAPEX | $15.53 B |
| Shared national factory | $651.8 M |
| Factory sizing basis | 5,502 modules for Luanda, then reused nationally |
| **Total national programme** | **$16.22 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $3.52 B (21.7%) |
| Domestic / local capital | $12.71 B (78.3%) |
| Annual external capital draw | $703.2 M / yr |
| Annual local capital draw | $2.54 B / yr |
| Annual public construction commitment | $1.84 B / yr for 5 years |
| Annual post-grace debt service | $1.40 B / yr |
| Default foreign-turnkey external capital | $29.20 B |
| External capital saved | $25.69 B |
| Capital + lifetime external interest saved | $57.27 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $7.28 B | $1.09 B | $6.19 B |
| Stations | $2.84 B | $567.1 M | $2.27 B |
| Depots | $902.6 M | $225.6 M | $676.9 M |
| Rolling stock | $2.44 B | $854.7 M | $1.59 B |
| Dedicated solar plants | $945.6 M | $425.5 M | $520.1 M |
| Residual train control | $40.0 M | $20.0 M | $20.0 M |
| Charging microgrids | $126.5 M | $50.6 M | $75.9 M |
| EPC / project services | $999.5 M | $149.9 M | $849.6 M |
| Shared national trainset factory | $651.8 M | $130.4 M | $521.4 M |
| **Total** | **$16.22 B** | **$3.52 B** | **$12.71 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital | Lines | Added lines | Original circles | Current circles |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| [Luanda](Luanda/README.md) | 9,085,000 | 917 | $9.08 B | $2.07 B | $7.00 B | 14 | 5 | 40.8% | 40.9% |
| [Huambo](Huambo/README.md) | 800,000 | 211 | $1.16 B | $239.1 M | $923.0 M | 5 | 2 | 20.5% | 28.6% |
| [Lubango](Lubango/README.md) | 700,000 | 223 | $1.32 B | $272.2 M | $1.05 B | 4 | 1 | 15.3% | 30.3% |
| [Benguela](Benguela/README.md) | 600,000 | 221 | $1.24 B | $257.2 M | $984.5 M | 5 | 2 | 30.4% | 40.4% |
| [Lobito](Lobito/README.md) | 500,000 | 134 | $770.7 M | $157.9 M | $612.7 M | 4 | 1 | 18.2% | 33.2% |
| [Malanje](Malanje/README.md) | 500,000 | 53 | $325.7 M | $67.4 M | $258.3 M | 2 | 0 | 12.9% | 11.6% |
| [Uige](Uige/README.md) | 400,000 | 39 | $218.4 M | $45.6 M | $172.8 M | 1 | 0 | 6.2% | 14.0% |
| [Namibe](Namibe/README.md) | 300,000 | 109 | $786.0 M | $146.5 M | $639.5 M | 5 | 2 | 43.6% | 40.3% |
| [Soyo](Soyo/README.md) | 250,000 | 85 | $624.3 M | $118.9 M | $505.3 M | 4 | 1 | 32.8% | 28.5% |

## Local Basis And Regeneration

Country finance parameters use `AO` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
