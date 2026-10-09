# Uganda National OpenSourceRail Strategy

This page contains only Uganda-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$32.89 B (88.7%) of external capital** and **$41.23 B of external interest**. Capital plus saved interest totals **$74.13 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 12 |
| Represented population | 4,925,000 |
| Trainsets / vehicle modules | 2,885 / 8,168 |
| City infrastructure and fleet CAPEX | $19.68 B |
| Shared national factory | $863.1 M |
| Factory sizing basis | 3,332 modules for Kampala, then reused nationally |
| **Total national programme** | **$20.60 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $4.19 B (20.4%) |
| Domestic / local capital | $16.41 B (79.6%) |
| Annual external capital draw | $599.1 M / yr |
| Annual local capital draw | $2.34 B / yr |
| Annual public construction commitment | $2.50 B / yr for 7 years |
| Annual post-grace debt service | $2.11 B / yr |
| Default foreign-turnkey external capital | $37.09 B |
| External capital saved | $32.89 B |
| Capital + lifetime external interest saved | $74.13 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $9.11 B | $1.37 B | $7.75 B |
| Stations | $4.21 B | $841.5 M | $3.37 B |
| Depots | $2.21 B | $552.7 M | $1.66 B |
| Rolling stock | $2.33 B | $815.8 M | $1.52 B |
| Dedicated solar plants | $373.2 M | $167.9 M | $205.2 M |
| Residual train control | $53.2 M | $26.6 M | $26.6 M |
| Charging microgrids | $126.6 M | $50.6 M | $76.0 M |
| EPC / project services | $1.32 B | $198.5 M | $1.12 B |
| Shared national trainset factory | $863.1 M | $172.6 M | $690.5 M |
| **Total** | **$20.60 B** | **$4.19 B** | **$16.41 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Kampala](Kampala/README.md) | 1,875,000 | 833 | $7.17 B | $1.52 B | $5.65 B |
| [Mbarara](Mbarara/README.md) | 500,000 | 349 | $1.86 B | $391.2 M | $1.46 B |
| [Gulu](Gulu/README.md) | 350,000 | 383 | $2.11 B | $446.0 M | $1.66 B |
| [Jinja](Jinja/README.md) | 300,000 | 244 | $1.56 B | $304.1 M | $1.25 B |
| [Mbale](Mbale/README.md) | 300,000 | 124 | $879.9 M | $167.7 M | $712.2 M |
| [Arua](Arua/README.md) | 250,000 | 176 | $1.10 B | $215.1 M | $885.8 M |
| [Entebbe](Entebbe/README.md) | 250,000 | 128 | $872.5 M | $168.3 M | $704.2 M |
| [Lira](Lira/README.md) | 250,000 | 192 | $1.18 B | $227.8 M | $951.2 M |
| [Masaka](Masaka/README.md) | 250,000 | 150 | $961.0 M | $186.1 M | $774.9 M |
| [Fort Portal](Fort-Portal/README.md) | 200,000 | 150 | $950.4 M | $185.7 M | $764.6 M |
| [Hoima](Hoima/README.md) | 200,000 | 126 | $860.4 M | $165.5 M | $694.9 M |
| [Soroti](Soroti/README.md) | 200,000 | 30 | $187.7 M | $37.6 M | $150.0 M |

## Local Basis And Regeneration

Country finance parameters use `UG` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

| City | Current lines | Added residential lines | Original station circles | Current station circles |
| --- | ---: | ---: | ---: | ---: |
| [Arua](Arua/README.md) | 12 | 9 | 33.3% | 69.8% |
| [Entebbe](Entebbe/README.md) | 8 | 5 | 46.6% | 77.6% |
| [Fort Portal](Fort-Portal/README.md) | 10 | 7 | 30.0% | 57.6% |
| [Gulu](Gulu/README.md) | 15 | 12 | 31.4% | 65.7% |
| [Hoima](Hoima/README.md) | 8 | 5 | 40.0% | 61.8% |
| [Jinja](Jinja/README.md) | 14 | 11 | 30.9% | 72.5% |
| [Kampala](Kampala/README.md) | 41 | 35 | 29.5% | 76.5% |
| [Lira](Lira/README.md) | 11 | 8 | 41.8% | 70.9% |
| [Masaka](Masaka/README.md) | 10 | 7 | 37.2% | 68.7% |
| [Mbale](Mbale/README.md) | 9 | 6 | 28.1% | 51.3% |
| [Mbarara](Mbarara/README.md) | 13 | 10 | 32.1% | 66.1% |
| [Soroti](Soroti/README.md) | 3 | 1 | 18.3% | 34.9% |

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
