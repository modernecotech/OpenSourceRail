# Mozambique National OpenSourceRail Strategy

This page contains only Mozambique-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$16.03 B (88.7%) of external capital** and **$20.71 B of external interest**. Capital plus saved interest totals **$36.75 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 10 |
| Represented population | 5,015,000 |
| Trainsets / vehicle modules | 1,229 / 3,726 |
| City infrastructure and fleet CAPEX | $9.06 B |
| Shared national factory | $917.1 M |
| Factory sizing basis | 1,208 modules for Maputo, then reused nationally |
| **Total national programme** | **$10.04 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $2.04 B (20.3%) |
| Domestic / local capital | $8.00 B (79.7%) |
| Annual external capital draw | $203.7 M / yr |
| Annual local capital draw | $800.3 M / yr |
| Annual public construction commitment | $1.12 B / yr for 10 years |
| Annual post-grace debt service | $1.01 B / yr |
| Default foreign-turnkey external capital | $18.07 B |
| External capital saved | $16.03 B |
| Capital + lifetime external interest saved | $36.75 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $4.80 B | $719.7 M | $4.08 B |
| Stations | $1.52 B | $303.8 M | $1.22 B |
| Depots | $663.5 M | $165.9 M | $497.6 M |
| Rolling stock | $1.08 B | $379.1 M | $704.0 M |
| Dedicated solar plants | $353.0 M | $158.8 M | $194.1 M |
| Residual train control | $26.5 M | $13.3 M | $13.3 M |
| Charging microgrids | $45.4 M | $18.1 M | $27.2 M |
| EPC / project services | $633.7 M | $95.1 M | $538.7 M |
| Shared national trainset factory | $917.1 M | $183.4 M | $733.7 M |
| **Total** | **$10.04 B** | **$2.04 B** | **$8.00 B** |

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
| [Lichinga](Lichinga/README.md) | 250,000 | 21 | $142.1 M | $27.6 M | $114.5 M | 2 | 0 | 17.9% | 17.9% |
| [Pemba Mz](Pemba-Mz/README.md) | 250,000 | 75 | $533.1 M | $101.1 M | $431.9 M | 4 | 1 | 37.7% | 50.1% |
| [Xai Xai](Xai-Xai/README.md) | 250,000 | 54 | $407.3 M | $77.0 M | $330.4 M | 4 | 1 | 41.7% | 38.5% |

## Local Basis And Regeneration

Country finance parameters use `MZ` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
