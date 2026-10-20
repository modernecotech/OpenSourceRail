# Mozambique National OpenSourceRail Strategy

This page contains only Mozambique-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$16.46 B (88.7%) of external capital** and **$21.26 B of external interest**. Capital plus saved interest totals **$37.72 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 10 |
| Represented population | 5,015,000 |
| Trainsets / vehicle modules | 1,259 / 3,786 |
| City infrastructure and fleet CAPEX | $9.32 B |
| Shared national factory | $917.1 M |
| Factory sizing basis | 1,208 modules for Maputo, then reused nationally |
| **Total national programme** | **$10.30 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $2.09 B (20.3%) |
| Domestic / local capital | $8.22 B (79.7%) |
| Annual external capital draw | $208.7 M / yr |
| Annual local capital draw | $821.7 M / yr |
| Annual public construction commitment | $1.15 B / yr for 10 years |
| Annual post-grace debt service | $1.04 B / yr |
| Default foreign-turnkey external capital | $18.55 B |
| External capital saved | $16.46 B |
| Capital + lifetime external interest saved | $37.72 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $4.93 B | $739.5 M | $4.19 B |
| Stations | $1.61 B | $321.5 M | $1.29 B |
| Depots | $667.5 M | $166.9 M | $500.7 M |
| Rolling stock | $1.10 B | $385.0 M | $714.9 M |
| Dedicated solar plants | $357.1 M | $160.7 M | $196.4 M |
| Residual train control | $27.2 M | $13.6 M | $13.6 M |
| Charging microgrids | $46.3 M | $18.5 M | $27.8 M |
| EPC / project services | $650.7 M | $97.6 M | $553.1 M |
| Shared national trainset factory | $917.1 M | $183.4 M | $733.7 M |
| **Total** | **$10.30 B** | **$2.09 B** | **$8.22 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital | Lines | Added lines | Original circles | Current circles |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| [Maputo](Maputo/README.md) | 1,530,000 | 302 | $3.27 B | $681.7 M | $2.59 B | 9 | 3 | 40.0% | 45.5% |
| [Nampula](Nampula/README.md) | 800,000 | 182 | $1.02 B | $213.0 M | $806.8 M | 5 | 2 | 23.3% | 31.6% |
| [Beira](Beira/README.md) | 535,000 | 164 | $897.8 M | $189.8 M | $708.0 M | 4 | 1 | 35.8% | 35.0% |
| [Chimoio](Chimoio/README.md) | 400,000 | 116 | $666.7 M | $138.5 M | $528.2 M | 3 | 1 | 25.0% | 26.3% |
| [Quelimane](Quelimane/README.md) | 350,000 | 32 | $174.4 M | $36.5 M | $137.8 M | 1 | 0 | 18.5% | 26.6% |
| [Tete](Tete/README.md) | 350,000 | 170 | $1.17 B | $230.7 M | $942.5 M | 5 | 2 | 23.0% | 24.6% |
| [Nacala](Nacala/README.md) | 300,000 | 113 | $771.0 M | $148.3 M | $622.7 M | 4 | 1 | 38.0% | 47.5% |
| [Lichinga](Lichinga/README.md) | 250,000 | 36 | $274.8 M | $51.9 M | $222.9 M | 2 | 0 | 17.9% | 19.5% |
| [Pemba Mz](Pemba-Mz/README.md) | 250,000 | 90 | $664.2 M | $126.3 M | $537.9 M | 4 | 1 | 37.7% | 46.1% |
| [Xai Xai](Xai-Xai/README.md) | 250,000 | 54 | $407.3 M | $77.0 M | $330.4 M | 4 | 1 | 41.7% | 38.5% |

## Local Basis And Regeneration

Country finance parameters use `MZ` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
