# Palestine National OpenSourceRail Strategy

This page contains only Palestine-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$9.03 B (88.3%) of external capital** and **$11.31 B of external interest**. Capital plus saved interest totals **$20.34 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 3 |
| Represented population | 1,850,000 |
| Trainsets / vehicle modules | 943 / 2,829 |
| City infrastructure and fleet CAPEX | $4.75 B |
| Shared national factory | $863.1 M |
| Factory sizing basis | 1,281 modules for Nablus, then reused nationally |
| **Total national programme** | **$5.68 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.19 B (21.0%) |
| Domestic / local capital | $4.48 B (79.0%) |
| Annual external capital draw | $170.4 M / yr |
| Annual local capital draw | $640.6 M / yr |
| Annual public construction commitment | $486.7 M / yr for 7 years |
| Annual post-grace debt service | $397.1 M / yr |
| Default foreign-turnkey external capital | $10.22 B |
| External capital saved | $9.03 B |
| Capital + lifetime external interest saved | $20.34 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $2.06 B | $309.2 M | $1.75 B |
| Stations | $915.2 M | $183.0 M | $732.2 M |
| Depots | $519.2 M | $129.8 M | $389.4 M |
| Rolling stock | $848.7 M | $297.0 M | $551.7 M |
| Dedicated solar plants | $73.8 M | $33.2 M | $40.6 M |
| Residual train control | $12.9 M | $6.4 M | $6.4 M |
| Charging microgrids | $16.1 M | $6.4 M | $9.7 M |
| EPC / project services | $366.6 M | $55.0 M | $311.6 M |
| Shared national trainset factory | $863.1 M | $172.6 M | $690.5 M |
| **Total** | **$5.68 B** | **$1.19 B** | **$4.48 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Hebron](Hebron/README.md) | 800,000 | 352 | $1.79 B | $378.6 M | $1.41 B |
| [Gaza City](Gaza-City/README.md) | 600,000 | 164 | $877.6 M | $184.2 M | $693.4 M |
| [Nablus](Nablus/README.md) | 450,000 | 427 | $2.09 B | $448.3 M | $1.64 B |

## Local Basis And Regeneration

Country finance parameters use `PS` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

| City | Current lines | Added residential lines | Original station circles | Current station circles |
| --- | ---: | ---: | ---: | ---: |
| [Gaza City](Gaza-City/README.md) | 6 | 3 | 57.2% | 83.5% |
| [Hebron](Hebron/README.md) | 13 | 10 | 29.4% | 77.0% |
| [Nablus](Nablus/README.md) | 14 | 11 | 37.9% | 78.6% |

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
