# Cameroon National OpenSourceRail Strategy

This page contains only Cameroon-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$42.07 B (87.9%) of external capital** and **$52.74 B of external interest**. Capital plus saved interest totals **$94.81 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 10 |
| Represented population | 11,650,000 |
| Trainsets / vehicle modules | 3,474 / 15,417 |
| City infrastructure and fleet CAPEX | $25.67 B |
| Shared national factory | $869.8 M |
| Factory sizing basis | 5,916 modules for Douala, then reused nationally |
| **Total national programme** | **$26.60 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $5.80 B (21.8%) |
| Domestic / local capital | $20.79 B (78.2%) |
| Annual external capital draw | $829.2 M / yr |
| Annual local capital draw | $2.97 B / yr |
| Annual public construction commitment | $2.27 B / yr for 7 years |
| Annual post-grace debt service | $1.86 B / yr |
| Default foreign-turnkey external capital | $47.88 B |
| External capital saved | $42.07 B |
| Capital + lifetime external interest saved | $94.81 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $11.56 B | $1.73 B | $9.82 B |
| Stations | $4.39 B | $877.5 M | $3.51 B |
| Depots | $2.18 B | $544.9 M | $1.63 B |
| Rolling stock | $4.42 B | $1.55 B | $2.87 B |
| Dedicated solar plants | $1.25 B | $563.5 M | $688.7 M |
| Residual train control | $60.0 M | $30.0 M | $30.0 M |
| Charging microgrids | $212.6 M | $85.0 M | $127.5 M |
| EPC / project services | $1.66 B | $248.7 M | $1.41 B |
| Shared national trainset factory | $869.8 M | $174.0 M | $695.8 M |
| **Total** | **$26.60 B** | **$5.80 B** | **$20.79 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Yaounde](Yaounde/README.md) | 4,100,000 | 691 | $6.42 B | $1.47 B | $4.95 B |
| [Douala](Douala/README.md) | 3,900,000 | 986 | $9.23 B | $2.08 B | $7.15 B |
| [Bafoussam](Bafoussam/README.md) | 600,000 | 416 | $2.19 B | $464.7 M | $1.73 B |
| [Bamenda](Bamenda/README.md) | 600,000 | 308 | $1.65 B | $348.7 M | $1.30 B |
| [Garoua](Garoua/README.md) | 600,000 | 179 | $1.09 B | $218.9 M | $873.4 M |
| [Maroua](Maroua/README.md) | 500,000 | 332 | $1.89 B | $383.6 M | $1.51 B |
| [Kumba](Kumba/README.md) | 400,000 | 258 | $1.35 B | $287.4 M | $1.07 B |
| [Bertoua](Bertoua/README.md) | 350,000 | 118 | $669.6 M | $139.0 M | $530.6 M |
| [Ngaoundere](Ngaoundere/README.md) | 350,000 | 150 | $882.5 M | $178.3 M | $704.2 M |
| [Edea](Edea/README.md) | 250,000 | 36 | $272.6 M | $50.4 M | $222.3 M |

## Local Basis And Regeneration

Country finance parameters use `CM` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

| City | Current lines | Added residential lines | Original station circles | Current station circles |
| --- | ---: | ---: | ---: | ---: |
| [Bafoussam](Bafoussam/README.md) | 15 | 12 | 21.2% | 58.9% |
| [Bamenda](Bamenda/README.md) | 13 | 10 | 24.3% | 54.6% |
| [Bertoua](Bertoua/README.md) | 5 | 2 | 18.4% | 34.5% |
| [Douala](Douala/README.md) | 33 | 28 | 30.3% | 71.5% |
| [Edea](Edea/README.md) | 2 | 1 | 15.2% | 37.4% |
| [Garoua](Garoua/README.md) | 8 | 5 | 18.6% | 45.1% |
| [Kumba](Kumba/README.md) | 11 | 8 | 19.2% | 48.3% |
| [Maroua](Maroua/README.md) | 13 | 10 | 30.1% | 61.3% |
| [Ngaoundere](Ngaoundere/README.md) | 7 | 4 | 23.9% | 46.6% |
| [Yaounde](Yaounde/README.md) | 21 | 16 | 27.3% | 82.1% |

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
