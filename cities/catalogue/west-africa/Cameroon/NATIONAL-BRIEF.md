# Cameroon National OpenSourceRail Strategy

This page contains only Cameroon-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$25.74 B (88.2%) of external capital** and **$32.27 B of external interest**. Capital plus saved interest totals **$58.00 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 10 |
| Represented population | 11,650,000 |
| Trainsets / vehicle modules | 1,828 / 7,795 |
| City infrastructure and fleet CAPEX | $15.13 B |
| Shared national factory | $1.02 B |
| Factory sizing basis | 2,604 modules for Yaounde, then reused nationally |
| **Total national programme** | **$16.22 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $3.46 B (21.3%) |
| Domestic / local capital | $12.76 B (78.7%) |
| Annual external capital draw | $494.2 M / yr |
| Annual local capital draw | $1.82 B / yr |
| Annual public construction commitment | $1.39 B / yr for 7 years |
| Annual post-grace debt service | $1.13 B / yr |
| Default foreign-turnkey external capital | $29.20 B |
| External capital saved | $25.74 B |
| Capital + lifetime external interest saved | $58.00 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $7.85 B | $1.18 B | $6.68 B |
| Stations | $2.10 B | $419.1 M | $1.68 B |
| Depots | $897.1 M | $224.3 M | $672.8 M |
| Rolling stock | $2.24 B | $785.6 M | $1.46 B |
| Dedicated solar plants | $980.7 M | $441.3 M | $539.4 M |
| Residual train control | $39.9 M | $20.0 M | $20.0 M |
| Charging microgrids | $93.9 M | $37.6 M | $56.3 M |
| EPC / project services | $997.0 M | $149.6 M | $847.5 M |
| Shared national trainset factory | $1.02 B | $203.6 M | $814.5 M |
| **Total** | **$16.22 B** | **$3.46 B** | **$12.76 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital | Lines | Added lines | Original circles | Current circles |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| [Yaounde](Yaounde/README.md) | 4,100,000 | 434 | $4.95 B | $1.09 B | $3.86 B | 8 | 3 | 27.3% | 30.3% |
| [Douala](Douala/README.md) | 3,900,000 | 342 | $4.12 B | $903.5 M | $3.22 B | 8 | 3 | 30.3% | 28.5% |
| [Bafoussam](Bafoussam/README.md) | 600,000 | 231 | $1.29 B | $270.2 M | $1.02 B | 5 | 2 | 21.2% | 23.6% |
| [Bamenda](Bamenda/README.md) | 600,000 | 168 | $965.7 M | $201.6 M | $764.1 M | 5 | 2 | 24.3% | 23.5% |
| [Garoua](Garoua/README.md) | 600,000 | 122 | $718.6 M | $146.0 M | $572.6 M | 4 | 1 | 18.6% | 24.5% |
| [Maroua](Maroua/README.md) | 500,000 | 193 | $1.11 B | $224.6 M | $881.0 M | 5 | 2 | 30.1% | 31.2% |
| [Kumba](Kumba/README.md) | 400,000 | 150 | $851.1 M | $177.5 M | $673.6 M | 4 | 1 | 19.2% | 25.5% |
| [Bertoua](Bertoua/README.md) | 350,000 | 80 | $461.1 M | $95.7 M | $365.4 M | 3 | 0 | 18.4% | 16.3% |
| [Ngaoundere](Ngaoundere/README.md) | 350,000 | 91 | $545.8 M | $110.1 M | $435.7 M | 4 | 1 | 23.9% | 25.0% |
| [Edea](Edea/README.md) | 250,000 | 17 | $125.8 M | $23.3 M | $102.5 M | 1 | 0 | 15.2% | 15.2% |

## Local Basis And Regeneration

Country finance parameters use `CM` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
