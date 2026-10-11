# Saudi Arabia National OpenSourceRail Strategy

This page contains only Saudi Arabia-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$89.90 B (88.1%) of external capital** and **$110.52 B of external interest**. Capital plus saved interest totals **$200.42 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 14 |
| Represented population | 15,600,000 |
| Trainsets / vehicle modules | 8,036 / 31,653 |
| City infrastructure and fleet CAPEX | $55.74 B |
| Shared national factory | $863.1 M |
| Factory sizing basis | 10,512 modules for Jeddah, then reused nationally |
| **Total national programme** | **$56.67 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $12.11 B (21.4%) |
| Domestic / local capital | $44.56 B (78.6%) |
| Annual external capital draw | $2.42 B / yr |
| Annual local capital draw | $8.91 B / yr |
| Annual public construction commitment | $3.93 B / yr for 5 years |
| Annual post-grace debt service | $2.73 B / yr |
| Default foreign-turnkey external capital | $102.00 B |
| External capital saved | $89.90 B |
| Capital + lifetime external interest saved | $200.42 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $24.78 B | $3.72 B | $21.06 B |
| Stations | $11.18 B | $2.24 B | $8.94 B |
| Depots | $4.73 B | $1.18 B | $3.55 B |
| Rolling stock | $9.10 B | $3.19 B | $5.92 B |
| Dedicated solar plants | $1.80 B | $808.5 M | $988.1 M |
| Residual train control | $147.7 M | $73.8 M | $73.8 M |
| Charging microgrids | $476.4 M | $190.6 M | $285.9 M |
| EPC / project services | $3.59 B | $538.4 M | $3.05 B |
| Shared national trainset factory | $863.1 M | $172.6 M | $690.5 M |
| **Total** | **$56.67 B** | **$12.11 B** | **$44.56 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Jeddah](Jeddah/README.md) | 4,700,000 | 1,752 | $15.11 B | $3.44 B | $11.67 B |
| [Mecca](Mecca/README.md) | 2,200,000 | 646 | $5.56 B | $1.15 B | $4.41 B |
| [Dammam](Dammam/README.md) | 1,500,000 | 918 | $7.81 B | $1.64 B | $6.17 B |
| [Medina](Medina/README.md) | 1,500,000 | 725 | $6.28 B | $1.30 B | $4.98 B |
| [Hofuf](Hofuf/README.md) | 800,000 | 503 | $2.60 B | $550.3 M | $2.05 B |
| [Buraidah](Buraidah/README.md) | 700,000 | 403 | $2.00 B | $423.7 M | $1.57 B |
| [Taif](Taif/README.md) | 700,000 | 391 | $1.86 B | $394.9 M | $1.46 B |
| [Tabuk](Tabuk/README.md) | 650,000 | 392 | $2.07 B | $431.7 M | $1.64 B |
| [Khamis Mushait](Khamis-Mushait/README.md) | 600,000 | 510 | $2.73 B | $572.0 M | $2.16 B |
| [Hail](Hail/README.md) | 500,000 | 392 | $2.02 B | $425.3 M | $1.60 B |
| [Najran](Najran/README.md) | 500,000 | 363 | $2.37 B | $470.2 M | $1.90 B |
| [Abha](Abha/README.md) | 450,000 | 348 | $1.76 B | $369.2 M | $1.39 B |
| [Al Kharj](Al-Kharj/README.md) | 400,000 | 402 | $2.06 B | $434.8 M | $1.63 B |
| [Jizan](Jizan/README.md) | 400,000 | 291 | $1.50 B | $316.2 M | $1.19 B |

## Local Basis And Regeneration

Country finance parameters use `SA` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

| City | Current lines | Added residential lines | Original station circles | Current station circles |
| --- | ---: | ---: | ---: | ---: |
| [Abha](Abha/README.md) | 10 | 7 | 16.2% | 55.4% |
| [Al Kharj](Al-Kharj/README.md) | 13 | 10 | 34.9% | 75.4% |
| [Buraidah](Buraidah/README.md) | 14 | 11 | 24.6% | 66.0% |
| [Dammam](Dammam/README.md) | 31 | 25 | 39.3% | 81.6% |
| [Hail](Hail/README.md) | 14 | 11 | 26.6% | 68.1% |
| [Hofuf](Hofuf/README.md) | 19 | 16 | 28.1% | 71.6% |
| [Jeddah](Jeddah/README.md) | 52 | 43 | 31.9% | 82.3% |
| [Jizan](Jizan/README.md) | 11 | 8 | 32.6% | 71.9% |
| [Khamis Mushait](Khamis-Mushait/README.md) | 17 | 14 | 32.3% | 68.0% |
| [Mecca](Mecca/README.md) | 27 | 21 | 35.7% | 80.0% |
| [Medina](Medina/README.md) | 35 | 29 | 25.1% | 80.1% |
| [Najran](Najran/README.md) | 13 | 10 | 25.3% | 71.4% |
| [Tabuk](Tabuk/README.md) | 12 | 9 | 28.2% | 65.8% |
| [Taif](Taif/README.md) | 13 | 10 | 22.8% | 61.3% |

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
