# Mozambique National OpenSourceRail Strategy

This page contains only Mozambique-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$24.50 B (88.6%) of external capital** and **$31.65 B of external interest**. Capital plus saved interest totals **$56.16 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 10 |
| Represented population | 5,015,000 |
| Trainsets / vehicle modules | 2,178 / 6,601 |
| City infrastructure and fleet CAPEX | $14.44 B |
| Shared national factory | $868.2 M |
| Factory sizing basis | 2,216 modules for Maputo, then reused nationally |
| **Total national programme** | **$15.37 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $3.16 B (20.6%) |
| Domestic / local capital | $12.21 B (79.4%) |
| Annual external capital draw | $316.1 M / yr |
| Annual local capital draw | $1.22 B / yr |
| Annual public construction commitment | $1.70 B / yr for 10 years |
| Annual post-grace debt service | $1.54 B / yr |
| Default foreign-turnkey external capital | $27.66 B |
| External capital saved | $24.50 B |
| Capital + lifetime external interest saved | $56.16 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $6.49 B | $974.1 M | $5.52 B |
| Stations | $3.16 B | $632.6 M | $2.53 B |
| Depots | $1.54 B | $385.6 M | $1.16 B |
| Rolling stock | $1.92 B | $670.8 M | $1.25 B |
| Dedicated solar plants | $266.1 M | $119.7 M | $146.3 M |
| Residual train control | $37.5 M | $18.8 M | $18.8 M |
| Charging microgrids | $93.8 M | $37.5 M | $56.2 M |
| EPC / project services | $988.0 M | $148.2 M | $839.8 M |
| Shared national trainset factory | $868.2 M | $173.6 M | $694.6 M |
| **Total** | **$15.37 B** | **$3.16 B** | **$12.21 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Maputo](Maputo/README.md) | 1,530,000 | 554 | $4.89 B | $1.04 B | $3.85 B |
| [Nampula](Nampula/README.md) | 800,000 | 312 | $1.74 B | $363.2 M | $1.38 B |
| [Beira](Beira/README.md) | 535,000 | 270 | $1.49 B | $313.3 M | $1.17 B |
| [Chimoio](Chimoio/README.md) | 400,000 | 210 | $1.15 B | $240.8 M | $904.9 M |
| [Quelimane](Quelimane/README.md) | 350,000 | 39 | $226.7 M | $46.9 M | $179.8 M |
| [Tete](Tete/README.md) | 350,000 | 306 | $1.97 B | $391.6 M | $1.58 B |
| [Nacala](Nacala/README.md) | 300,000 | 220 | $1.26 B | $247.1 M | $1.01 B |
| [Lichinga](Lichinga/README.md) | 250,000 | 43 | $282.5 M | $55.3 M | $227.2 M |
| [Pemba Mz](Pemba-Mz/README.md) | 250,000 | 131 | $843.4 M | $163.7 M | $679.7 M |
| [Xai Xai](Xai-Xai/README.md) | 250,000 | 93 | $594.7 M | $115.9 M | $478.8 M |

## Local Basis And Regeneration

Country finance parameters use `MZ` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

| City | Current lines | Added residential lines | Original station circles | Current station circles |
| --- | ---: | ---: | ---: | ---: |
| [Beira](Beira/README.md) | 13 | 10 | 35.8% | 74.8% |
| [Chimoio](Chimoio/README.md) | 7 | 5 | 25.0% | 57.8% |
| [Lichinga](Lichinga/README.md) | 4 | 2 | 17.9% | 29.7% |
| [Maputo](Maputo/README.md) | 23 | 17 | 40.0% | 79.5% |
| [Nacala](Nacala/README.md) | 13 | 10 | 38.0% | 78.1% |
| [Nampula](Nampula/README.md) | 16 | 13 | 23.3% | 63.6% |
| [Pemba Mz](Pemba-Mz/README.md) | 8 | 5 | 37.7% | 80.1% |
| [Quelimane](Quelimane/README.md) | 2 | 1 | 18.5% | 34.6% |
| [Tete](Tete/README.md) | 12 | 9 | 23.0% | 64.4% |
| [Xai Xai](Xai-Xai/README.md) | 7 | 4 | 41.7% | 63.9% |

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
