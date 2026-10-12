# Saudi Arabia National OpenSourceRail Strategy

This page contains only Saudi Arabia-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$51.06 B (88.4%) of external capital** and **$62.78 B of external interest**. Capital plus saved interest totals **$113.83 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 14 |
| Represented population | 15,600,000 |
| Trainsets / vehicle modules | 4,060 / 15,237 |
| City infrastructure and fleet CAPEX | $31.15 B |
| Shared national factory | $863.1 M |
| Factory sizing basis | 4,212 modules for Jeddah, then reused nationally |
| **Total national programme** | **$32.07 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $6.67 B (20.8%) |
| Domestic / local capital | $25.40 B (79.2%) |
| Annual external capital draw | $1.33 B / yr |
| Annual local capital draw | $5.08 B / yr |
| Annual public construction commitment | $2.23 B / yr for 5 years |
| Annual post-grace debt service | $1.55 B / yr |
| Default foreign-turnkey external capital | $57.73 B |
| External capital saved | $51.06 B |
| Capital + lifetime external interest saved | $113.83 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $17.23 B | $2.59 B | $14.65 B |
| Stations | $3.93 B | $785.6 M | $3.14 B |
| Depots | $1.76 B | $440.1 M | $1.32 B |
| Rolling stock | $4.41 B | $1.54 B | $2.87 B |
| Dedicated solar plants | $1.63 B | $731.3 M | $893.8 M |
| Residual train control | $97.0 M | $48.5 M | $48.5 M |
| Charging microgrids | $161.8 M | $64.7 M | $97.0 M |
| EPC / project services | $1.99 B | $298.8 M | $1.69 B |
| Shared national trainset factory | $863.1 M | $172.6 M | $690.5 M |
| **Total** | **$32.07 B** | **$6.67 B** | **$25.40 B** |

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
| [Khamis Mushait](Khamis-Mushait/README.md) | 600,000 | 320 | $1.72 B | $359.9 M | $1.36 B | 5 | 2 | 32.3% | 40.8% |
| [Hail](Hail/README.md) | 500,000 | 246 | $1.34 B | $280.1 M | $1.06 B | 5 | 2 | 26.6% | 31.3% |
| [Najran](Najran/README.md) | 500,000 | 213 | $1.28 B | $258.6 M | $1.02 B | 5 | 2 | 25.3% | 30.0% |
| [Abha](Abha/README.md) | 450,000 | 229 | $1.15 B | $241.4 M | $908.6 M | 4 | 1 | 16.2% | 24.2% |
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
