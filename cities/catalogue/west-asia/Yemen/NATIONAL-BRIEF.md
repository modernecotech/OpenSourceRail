# Yemen National OpenSourceRail Strategy

This page contains only Yemen-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$20.42 B (88.3%) of external capital** and **$26.38 B of external interest**. Capital plus saved interest totals **$46.80 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 9 |
| Represented population | 8,337,500 |
| Trainsets / vehicle modules | 1,643 / 6,413 |
| City infrastructure and fleet CAPEX | $12.06 B |
| Shared national factory | $733.3 M |
| Factory sizing basis | 3,384 modules for Sanaa, then reused nationally |
| **Total national programme** | **$12.84 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $2.70 B (21.0%) |
| Domestic / local capital | $10.15 B (79.0%) |
| Annual external capital draw | $269.7 M / yr |
| Annual local capital draw | $1.01 B / yr |
| Annual public construction commitment | $1.79 B / yr for 10 years |
| Annual post-grace debt service | $1.64 B / yr |
| Default foreign-turnkey external capital | $23.12 B |
| External capital saved | $20.42 B |
| Capital + lifetime external interest saved | $46.80 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $5.92 B | $887.6 M | $5.03 B |
| Stations | $2.10 B | $420.8 M | $1.68 B |
| Depots | $843.6 M | $210.9 M | $632.7 M |
| Rolling stock | $1.85 B | $646.8 M | $1.20 B |
| Dedicated solar plants | $479.0 M | $215.6 M | $263.5 M |
| Residual train control | $32.3 M | $16.1 M | $16.1 M |
| Charging microgrids | $77.0 M | $30.8 M | $46.2 M |
| EPC / project services | $808.9 M | $121.3 M | $687.6 M |
| Shared national trainset factory | $733.3 M | $146.7 M | $586.6 M |
| **Total** | **$12.84 B** | **$2.70 B** | **$10.15 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital | Lines | Added lines | Original circles | Current circles |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| [Sanaa](Sanaa/README.md) | 3,937,500 | 564 | $5.69 B | $1.25 B | $4.44 B | 11 | 4 | 61.4% | 53.6% |
| [Aden](Aden/README.md) | 985,000 | 182 | $966.9 M | $202.6 M | $764.3 M | 5 | 2 | 45.6% | 50.7% |
| [Hodeidah](Hodeidah/README.md) | 750,000 | 106 | $608.7 M | $124.3 M | $484.4 M | 4 | 1 | 39.3% | 45.1% |
| [Ibb](Ibb/README.md) | 750,000 | 157 | $887.6 M | $181.4 M | $706.2 M | 5 | 2 | 21.0% | 14.6% |
| [Taiz](Taiz/README.md) | 615,000 | 172 | $1.02 B | $207.9 M | $809.0 M | 5 | 2 | 36.3% | 36.6% |
| [Mukalla](Mukalla/README.md) | 550,000 | 254 | $1.41 B | $293.9 M | $1.12 B | 5 | 2 | 49.7% | 59.7% |
| [Dhamar](Dhamar/README.md) | 300,000 | 77 | $524.3 M | $98.9 M | $425.4 M | 4 | 1 | 34.5% | 51.0% |
| [Lahij](Lahij/README.md) | 250,000 | 68 | $512.4 M | $95.6 M | $416.8 M | 4 | 1 | 54.9% | 62.1% |
| [Sayun](Sayun/README.md) | 200,000 | 63 | $441.8 M | $83.3 M | $358.5 M | 4 | 1 | 57.4% | 48.7% |

## Local Basis And Regeneration

Country finance parameters use `YE` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
