# Indonesia National OpenSourceRail Strategy

This page contains only Indonesia-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$15.93 B (87.9%) of external capital** and **$19.58 B of external interest**. Capital plus saved interest totals **$35.51 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 2 |
| Represented population | 5,624,000 |
| Trainsets / vehicle modules | 880 / 4,600 |
| City infrastructure and fleet CAPEX | $9.58 B |
| Shared national factory | $454.5 M |
| Factory sizing basis | 3,240 modules for Surabaya, then reused nationally |
| **Total national programme** | **$10.06 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $2.18 B (21.7%) |
| Domestic / local capital | $7.88 B (78.3%) |
| Annual external capital draw | $436.9 M / yr |
| Annual local capital draw | $1.58 B / yr |
| Annual public construction commitment | $835.7 M / yr for 5 years |
| Annual post-grace debt service | $596.0 M / yr |
| Default foreign-turnkey external capital | $18.11 B |
| External capital saved | $15.93 B |
| Capital + lifetime external interest saved | $35.51 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $4.50 B | $675.1 M | $3.83 B |
| Stations | $1.95 B | $390.7 M | $1.56 B |
| Depots | $381.7 M | $95.4 M | $286.2 M |
| Rolling stock | $1.29 B | $450.8 M | $837.2 M |
| Dedicated solar plants | $751.6 M | $338.2 M | $413.4 M |
| Residual train control | $25.5 M | $12.7 M | $12.7 M |
| Charging microgrids | $97.8 M | $39.1 M | $58.7 M |
| EPC / project services | $609.1 M | $91.4 M | $517.8 M |
| Shared national trainset factory | $454.5 M | $90.9 M | $363.6 M |
| **Total** | **$10.06 B** | **$2.18 B** | **$7.88 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Surabaya](Surabaya/README.md) | 3,009,000 | 540 | $5.81 B | $1.31 B | $4.50 B |
| [Bandung](Bandung/README.md) | 2,615,000 | 340 | $3.77 B | $782.7 M | $2.98 B |

## Local Basis And Regeneration

Country finance parameters use `ID` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

| City | Current lines | Added residential lines | Original station circles | Current station circles |
| --- | ---: | ---: | ---: | ---: |
| [Bandung](Bandung/README.md) | 6 | 0 | Unavailable | Unavailable |
| [Surabaya](Surabaya/README.md) | 9 | 0 | Unavailable | Unavailable |

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
