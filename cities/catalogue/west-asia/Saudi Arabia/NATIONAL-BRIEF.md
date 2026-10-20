# Saudi Arabia National OpenSourceRail Strategy

This page contains only Saudi Arabia-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$51.29 B (88.4%) of external capital** and **$63.06 B of external interest**. Capital plus saved interest totals **$114.36 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 14 |
| Represented population | 15,600,000 |
| Trainsets / vehicle modules | 4,088 / 15,321 |
| City infrastructure and fleet CAPEX | $31.30 B |
| Shared national factory | $863.1 M |
| Factory sizing basis | 4,212 modules for Jeddah, then reused nationally |
| **Total national programme** | **$32.22 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $6.70 B (20.8%) |
| Domestic / local capital | $25.52 B (79.2%) |
| Annual external capital draw | $1.34 B / yr |
| Annual local capital draw | $5.10 B / yr |
| Annual public construction commitment | $2.24 B / yr for 5 years |
| Annual post-grace debt service | $1.55 B / yr |
| Default foreign-turnkey external capital | $58.00 B |
| External capital saved | $51.29 B |
| Capital + lifetime external interest saved | $114.36 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $17.29 B | $2.59 B | $14.69 B |
| Stations | $3.98 B | $795.5 M | $3.18 B |
| Depots | $1.77 B | $441.3 M | $1.32 B |
| Rolling stock | $4.44 B | $1.55 B | $2.88 B |
| Dedicated solar plants | $1.63 B | $733.2 M | $896.2 M |
| Residual train control | $97.3 M | $48.7 M | $48.7 M |
| Charging microgrids | $162.8 M | $65.1 M | $97.7 M |
| EPC / project services | $2.00 B | $300.2 M | $1.70 B |
| Shared national trainset factory | $863.1 M | $172.6 M | $690.5 M |
| **Total** | **$32.22 B** | **$6.70 B** | **$25.52 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital | Lines | Added lines | Original circles | Current circles |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| [Jeddah](Jeddah/README.md) | 4,700,000 | 702 | $7.29 B | $1.61 B | $5.68 B | 14 | 5 | 31.9% | 34.0% |
| [Mecca](Mecca/README.md) | 2,200,000 | 315 | $3.68 B | $731.3 M | $2.95 B | 9 | 3 | 35.7% | 31.8% |
| [Dammam](Dammam/README.md) | 1,500,000 | 381 | $4.41 B | $886.4 M | $3.53 B | 9 | 3 | 39.3% | 31.7% |
| [Medina](Medina/README.md) | 1,500,000 | 255 | $3.05 B | $604.9 M | $2.44 B | 9 | 3 | 25.1% | 25.8% |
| [Hofuf](Hofuf/README.md) | 800,000 | 267 | $1.32 B | $280.1 M | $1.04 B | 5 | 2 | 28.1% | 29.8% |
| [Buraidah](Buraidah/README.md) | 700,000 | 249 | $1.30 B | $271.2 M | $1.03 B | 5 | 2 | 24.6% | 24.2% |
| [Taif](Taif/README.md) | 700,000 | 220 | $1.14 B | $239.3 M | $902.6 M | 5 | 2 | 22.8% | 22.4% |
| [Tabuk](Tabuk/README.md) | 650,000 | 237 | $1.24 B | $258.1 M | $977.3 M | 5 | 2 | 28.2% | 26.8% |
| [Khamis Mushait](Khamis-Mushait/README.md) | 600,000 | 333 | $1.76 B | $369.9 M | $1.39 B | 5 | 2 | 32.3% | 43.5% |
| [Hail](Hail/README.md) | 500,000 | 246 | $1.34 B | $280.1 M | $1.06 B | 5 | 2 | 26.6% | 31.3% |
| [Najran](Najran/README.md) | 500,000 | 213 | $1.28 B | $258.6 M | $1.02 B | 5 | 2 | 25.3% | 30.0% |
| [Abha](Abha/README.md) | 450,000 | 244 | $1.26 B | $263.3 M | $996.9 M | 4 | 1 | 16.2% | 30.0% |
| [Al Kharj](Al-Kharj/README.md) | 400,000 | 232 | $1.20 B | $251.8 M | $949.9 M | 5 | 2 | 34.9% | 34.8% |
| [Jizan](Jizan/README.md) | 400,000 | 194 | $1.02 B | $214.9 M | $805.6 M | 5 | 2 | 32.6% | 32.5% |

## Local Basis And Regeneration

Country finance parameters use `SA` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
