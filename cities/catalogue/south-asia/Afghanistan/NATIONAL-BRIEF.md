# Afghanistan National OpenSourceRail Strategy

This page contains only Afghanistan-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$20.38 B (88.1%) of external capital** and **$26.32 B of external interest**. Capital plus saved interest totals **$46.70 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 5 |
| Represented population | 7,051,000 |
| Trainsets / vehicle modules | 1,777 / 7,290 |
| City infrastructure and fleet CAPEX | $11.94 B |
| Shared national factory | $846.7 M |
| Factory sizing basis | 3,918 modules for Kabul, then reused nationally |
| **Total national programme** | **$12.85 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $2.75 B (21.4%) |
| Domestic / local capital | $10.10 B (78.6%) |
| Annual external capital draw | $274.9 M / yr |
| Annual local capital draw | $1.01 B / yr |
| Annual public construction commitment | $1.78 B / yr for 10 years |
| Annual post-grace debt service | $1.63 B / yr |
| Default foreign-turnkey external capital | $23.13 B |
| External capital saved | $20.38 B |
| Capital + lifetime external interest saved | $46.70 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $5.42 B | $813.7 M | $4.61 B |
| Stations | $2.11 B | $422.9 M | $1.69 B |
| Depots | $1.03 B | $257.5 M | $772.4 M |
| Rolling stock | $2.11 B | $738.0 M | $1.37 B |
| Dedicated solar plants | $386.5 M | $173.9 M | $212.6 M |
| Residual train control | $29.9 M | $15.0 M | $15.0 M |
| Charging microgrids | $92.2 M | $36.9 M | $55.3 M |
| EPC / project services | $815.2 M | $122.3 M | $693.0 M |
| Shared national trainset factory | $846.7 M | $169.3 M | $677.4 M |
| **Total** | **$12.85 B** | **$2.75 B** | **$10.10 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Kabul](Kabul/README.md) | 4,601,000 | 653 | $6.04 B | $1.34 B | $4.70 B |
| [Herat](Herat/README.md) | 800,000 | 284 | $1.45 B | $300.6 M | $1.14 B |
| [Kandahar](Kandahar/README.md) | 700,000 | 297 | $1.63 B | $336.9 M | $1.29 B |
| [Mazar E Sharif](Mazar-E-Sharif/README.md) | 600,000 | 252 | $1.32 B | $275.6 M | $1.04 B |
| [Jalalabad Af](Jalalabad-Af/README.md) | 350,000 | 291 | $1.52 B | $316.2 M | $1.20 B |

## Local Basis And Regeneration

Country finance parameters use `AF` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

| City | Current lines | Added residential lines | Original station circles | Current station circles |
| --- | ---: | ---: | ---: | ---: |
| [Herat](Herat/README.md) | 10 | 7 | 18.8% | 48.1% |
| [Jalalabad Af](Jalalabad-Af/README.md) | 10 | 7 | 31.3% | 74.2% |
| [Kabul](Kabul/README.md) | 22 | 15 | 40.8% | 80.3% |
| [Kandahar](Kandahar/README.md) | 12 | 9 | 27.0% | 74.6% |
| [Mazar E Sharif](Mazar-E-Sharif/README.md) | 6 | 3 | 44.3% | 77.9% |

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
