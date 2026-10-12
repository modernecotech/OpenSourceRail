# Pakistan National OpenSourceRail Strategy

This page contains only Pakistan-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$55.74 B (88.6%) of external capital** and **$69.88 B of external interest**. Capital plus saved interest totals **$125.62 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 13 |
| Represented population | 37,603,000 |
| Trainsets / vehicle modules | 3,469 / 15,345 |
| City infrastructure and fleet CAPEX | $33.88 B |
| Shared national factory | $1.02 B |
| Factory sizing basis | 5,526 modules for Karachi, then reused nationally |
| **Total national programme** | **$34.97 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $7.20 B (20.6%) |
| Domestic / local capital | $27.77 B (79.4%) |
| Annual external capital draw | $1.03 B / yr |
| Annual local capital draw | $3.97 B / yr |
| Annual public construction commitment | $4.78 B / yr for 7 years |
| Annual post-grace debt service | $4.11 B / yr |
| Default foreign-turnkey external capital | $62.94 B |
| External capital saved | $55.74 B |
| Capital + lifetime external interest saved | $125.62 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $18.60 B | $2.79 B | $15.81 B |
| Stations | $5.06 B | $1.01 B | $4.05 B |
| Depots | $1.71 B | $426.9 M | $1.28 B |
| Rolling stock | $4.36 B | $1.52 B | $2.83 B |
| Dedicated solar plants | $1.72 B | $772.2 M | $943.8 M |
| Residual train control | $96.6 M | $48.3 M | $48.3 M |
| Charging microgrids | $238.9 M | $95.6 M | $143.4 M |
| EPC / project services | $2.18 B | $326.3 M | $1.85 B |
| Shared national trainset factory | $1.02 B | $203.6 M | $814.5 M |
| **Total** | **$34.97 B** | **$7.20 B** | **$27.77 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital | Lines | Added lines | Original circles | Current circles |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| [Karachi](Karachi/README.md) | 20,300,000 | 921 | $10.17 B | $2.20 B | $7.97 B | 14 | 5 | 47.7% | 44.8% |
| [Faisalabad](Faisalabad/README.md) | 3,556,000 | 317 | $3.42 B | $742.1 M | $2.68 B | 9 | 3 | 40.9% | 45.8% |
| [Gujranwala](Gujranwala/README.md) | 2,300,000 | 261 | $2.84 B | $572.0 M | $2.27 B | 8 | 3 | 29.1% | 32.4% |
| [Peshawar](Peshawar/README.md) | 2,300,000 | 257 | $3.09 B | $608.6 M | $2.49 B | 8 | 3 | 24.3% | 21.5% |
| [Multan](Multan/README.md) | 2,197,000 | 199 | $2.29 B | $453.3 M | $1.83 B | 8 | 3 | 34.3% | 38.8% |
| [Hyderabad Pk](Hyderabad-Pk/README.md) | 1,900,000 | 362 | $3.90 B | $782.1 M | $3.12 B | 9 | 3 | 49.4% | 56.1% |
| [Quetta](Quetta/README.md) | 1,200,000 | 145 | $1.92 B | $372.1 M | $1.55 B | 6 | 2 | 32.0% | 34.5% |
| [Bahawalpur](Bahawalpur/README.md) | 900,000 | 171 | $973.4 M | $200.6 M | $772.8 M | 5 | 2 | 35.6% | 39.3% |
| [Sialkot](Sialkot/README.md) | 750,000 | 197 | $1.38 B | $267.4 M | $1.11 B | 5 | 2 | 28.1% | 31.5% |
| [Sheikhupura](Sheikhupura/README.md) | 600,000 | 118 | $603.3 M | $130.3 M | $473.1 M | 2 | 0 | 14.9% | 14.9% |
| [Sukkur](Sukkur/README.md) | 600,000 | 165 | $1.16 B | $225.1 M | $933.4 M | 4 | 1 | 28.9% | 40.5% |
| [Larkana](Larkana/README.md) | 500,000 | 127 | $918.9 M | $176.6 M | $742.3 M | 3 | 1 | 22.2% | 35.2% |
| [Rahim Yar Khan](Rahim-Yar-Khan/README.md) | 500,000 | 229 | $1.21 B | $252.5 M | $954.7 M | 5 | 2 | 20.7% | 41.3% |

## Local Basis And Regeneration

Country finance parameters use `PK` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
