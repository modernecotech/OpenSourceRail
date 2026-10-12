# Uganda National OpenSourceRail Strategy

This page contains only Uganda-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$21.14 B (89.0%) of external capital** and **$26.50 B of external interest**. Capital plus saved interest totals **$47.64 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 12 |
| Represented population | 4,925,000 |
| Trainsets / vehicle modules | 1,609 / 4,403 |
| City infrastructure and fleet CAPEX | $12.40 B |
| Shared national factory | $750.0 M |
| Factory sizing basis | 1,444 modules for Kampala, then reused nationally |
| **Total national programme** | **$13.20 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $2.62 B (19.9%) |
| Domestic / local capital | $10.58 B (80.1%) |
| Annual external capital draw | $374.8 M / yr |
| Annual local capital draw | $1.51 B / yr |
| Annual public construction commitment | $1.61 B / yr for 7 years |
| Annual post-grace debt service | $1.35 B / yr |
| Default foreign-turnkey external capital | $23.76 B |
| External capital saved | $21.14 B |
| Capital + lifetime external interest saved | $47.64 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $6.74 B | $1.01 B | $5.73 B |
| Stations | $2.24 B | $448.3 M | $1.79 B |
| Depots | $848.9 M | $212.2 M | $636.7 M |
| Rolling stock | $1.26 B | $441.2 M | $819.4 M |
| Dedicated solar plants | $428.9 M | $193.0 M | $235.9 M |
| Residual train control | $36.3 M | $18.1 M | $18.1 M |
| Charging microgrids | $60.9 M | $24.4 M | $36.6 M |
| EPC / project services | $835.7 M | $125.3 M | $710.3 M |
| Shared national trainset factory | $750.0 M | $150.0 M | $600.0 M |
| **Total** | **$13.20 B** | **$2.62 B** | **$10.58 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital | Lines | Added lines | Original circles | Current circles |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| [Kampala](Kampala/README.md) | 1,875,000 | 361 | $4.03 B | $824.4 M | $3.20 B | 9 | 3 | 29.5% | 30.9% |
| [Mbarara](Mbarara/README.md) | 500,000 | 202 | $1.15 B | $239.7 M | $906.1 M | 4 | 1 | 32.1% | 39.4% |
| [Gulu](Gulu/README.md) | 350,000 | 261 | $1.47 B | $311.4 M | $1.16 B | 5 | 2 | 31.4% | 36.6% |
| [Jinja](Jinja/README.md) | 300,000 | 121 | $930.8 M | $176.4 M | $754.3 M | 4 | 1 | 30.9% | 36.7% |
| [Mbale](Mbale/README.md) | 300,000 | 95 | $705.3 M | $132.4 M | $572.9 M | 5 | 2 | 28.1% | 33.1% |
| [Arua](Arua/README.md) | 250,000 | 98 | $721.9 M | $136.7 M | $585.2 M | 4 | 1 | 33.3% | 31.7% |
| [Entebbe](Entebbe/README.md) | 250,000 | 110 | $797.6 M | $152.6 M | $645.0 M | 4 | 1 | 46.6% | 54.6% |
| [Lira](Lira/README.md) | 250,000 | 92 | $627.8 M | $119.3 M | $508.5 M | 4 | 1 | 41.8% | 42.6% |
| [Masaka](Masaka/README.md) | 250,000 | 83 | $626.0 M | $117.9 M | $508.1 M | 4 | 1 | 37.2% | 36.3% |
| [Fort Portal](Fort-Portal/README.md) | 200,000 | 85 | $621.0 M | $116.4 M | $504.6 M | 4 | 1 | 30.0% | 35.2% |
| [Hoima](Hoima/README.md) | 200,000 | 71 | $523.9 M | $98.4 M | $425.5 M | 4 | 1 | 40.0% | 44.4% |
| [Soroti](Soroti/README.md) | 200,000 | 30 | $201.3 M | $40.0 M | $161.4 M | 2 | 0 | 18.3% | 21.2% |

## Local Basis And Regeneration

Country finance parameters use `UG` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
