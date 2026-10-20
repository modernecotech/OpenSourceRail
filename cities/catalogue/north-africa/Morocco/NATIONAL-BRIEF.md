# Morocco National OpenSourceRail Strategy

This page contains only Morocco-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$29.96 B (88.8%) of external capital** and **$36.83 B of external interest**. Capital plus saved interest totals **$66.79 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 12 |
| Represented population | 8,050,000 |
| Trainsets / vehicle modules | 2,268 / 7,477 |
| City infrastructure and fleet CAPEX | $17.78 B |
| Shared national factory | $912.3 M |
| Factory sizing basis | 1,492 modules for Marrakech, then reused nationally |
| **Total national programme** | **$18.75 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $3.80 B (20.2%) |
| Domestic / local capital | $14.96 B (79.8%) |
| Annual external capital draw | $759.1 M / yr |
| Annual local capital draw | $2.99 B / yr |
| Annual public construction commitment | $1.31 B / yr for 5 years |
| Annual post-grace debt service | $902.6 M / yr |
| Default foreign-turnkey external capital | $33.75 B |
| External capital saved | $29.96 B |
| Capital + lifetime external interest saved | $66.79 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $9.48 B | $1.42 B | $8.05 B |
| Stations | $3.14 B | $627.9 M | $2.51 B |
| Depots | $1.07 B | $266.3 M | $798.9 M |
| Rolling stock | $2.16 B | $757.1 M | $1.41 B |
| Dedicated solar plants | $653.3 M | $294.0 M | $359.3 M |
| Residual train control | $51.1 M | $25.5 M | $25.5 M |
| Charging microgrids | $107.8 M | $43.1 M | $64.7 M |
| EPC / project services | $1.18 B | $177.6 M | $1.01 B |
| Shared national trainset factory | $912.3 M | $182.5 M | $729.9 M |
| **Total** | **$18.75 B** | **$3.80 B** | **$14.96 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital | Lines | Added lines | Original circles | Current circles |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| [Fez](Fez/README.md) | 1,300,000 | 218 | $2.63 B | $523.8 M | $2.11 B | 6 | 2 | 46.0% | 53.7% |
| [Marrakech](Marrakech/README.md) | 1,200,000 | 373 | $3.89 B | $787.5 M | $3.10 B | 9 | 3 | 41.2% | 57.5% |
| [Tangier](Tangier/README.md) | 1,200,000 | 299 | $3.33 B | $671.5 M | $2.66 B | 8 | 3 | 57.5% | 49.8% |
| [Agadir](Agadir/README.md) | 900,000 | 298 | $1.53 B | $321.0 M | $1.21 B | 5 | 2 | 46.8% | 51.7% |
| [Meknes](Meknes/README.md) | 700,000 | 158 | $925.7 M | $191.1 M | $734.5 M | 5 | 2 | 38.9% | 37.4% |
| [Oujda](Oujda/README.md) | 600,000 | 123 | $711.9 M | $145.5 M | $566.4 M | 4 | 1 | 51.7% | 47.1% |
| [Kenitra](Kenitra/README.md) | 500,000 | 229 | $1.23 B | $259.2 M | $970.1 M | 4 | 1 | 50.8% | 51.2% |
| [Tetouan](Tetouan/README.md) | 500,000 | 205 | $1.22 B | $251.2 M | $972.3 M | 4 | 1 | 40.4% | 56.1% |
| [Safi](Safi/README.md) | 350,000 | 148 | $789.6 M | $164.8 M | $624.8 M | 4 | 1 | 67.8% | 69.7% |
| [Beni Mellal](Beni-Mellal/README.md) | 300,000 | 69 | $468.7 M | $88.3 M | $380.4 M | 4 | 1 | 59.0% | 59.4% |
| [Khouribga](Khouribga/README.md) | 250,000 | 56 | $387.7 M | $74.6 M | $313.1 M | 3 | 0 | 49.3% | 70.2% |
| [Nador](Nador/README.md) | 250,000 | 92 | $663.5 M | $124.7 M | $538.8 M | 4 | 1 | 47.2% | 53.6% |

## Local Basis And Regeneration

Country finance parameters use `MA` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
