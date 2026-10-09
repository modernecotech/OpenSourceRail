# Morocco National OpenSourceRail Strategy

This page contains only Morocco-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$29.61 B (88.7%) of external capital** and **$36.41 B of external interest**. Capital plus saved interest totals **$66.02 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 12 |
| Represented population | 8,050,000 |
| Trainsets / vehicle modules | 2,478 / 8,051 |
| City infrastructure and fleet CAPEX | $17.63 B |
| Shared national factory | $863.1 M |
| Factory sizing basis | 1,736 modules for Marrakech, then reused nationally |
| **Total national programme** | **$18.55 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $3.78 B (20.4%) |
| Domestic / local capital | $14.77 B (79.6%) |
| Annual external capital draw | $755.7 M / yr |
| Annual local capital draw | $2.95 B / yr |
| Annual public construction commitment | $1.29 B / yr for 5 years |
| Annual post-grace debt service | $893.2 M / yr |
| Default foreign-turnkey external capital | $33.39 B |
| External capital saved | $29.61 B |
| Capital + lifetime external interest saved | $66.02 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $8.90 B | $1.34 B | $7.57 B |
| Stations | $3.20 B | $639.3 M | $2.56 B |
| Depots | $1.46 B | $364.9 M | $1.09 B |
| Rolling stock | $2.33 B | $817.1 M | $1.52 B |
| Dedicated solar plants | $449.4 M | $202.2 M | $247.2 M |
| Residual train control | $48.8 M | $24.4 M | $24.4 M |
| Charging microgrids | $112.9 M | $45.1 M | $67.7 M |
| EPC / project services | $1.18 B | $177.6 M | $1.01 B |
| Shared national trainset factory | $863.1 M | $172.6 M | $690.5 M |
| **Total** | **$18.55 B** | **$3.78 B** | **$14.77 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Fez](Fez/README.md) | 1,300,000 | 200 | $2.04 B | $410.4 M | $1.63 B |
| [Marrakech](Marrakech/README.md) | 1,200,000 | 434 | $4.00 B | $818.3 M | $3.18 B |
| [Tangier](Tangier/README.md) | 1,200,000 | 245 | $2.57 B | $519.2 M | $2.05 B |
| [Agadir](Agadir/README.md) | 900,000 | 340 | $1.68 B | $356.3 M | $1.32 B |
| [Meknes](Meknes/README.md) | 700,000 | 182 | $1.07 B | $218.1 M | $847.0 M |
| [Oujda](Oujda/README.md) | 600,000 | 127 | $757.7 M | $154.3 M | $603.4 M |
| [Kenitra](Kenitra/README.md) | 500,000 | 276 | $1.36 B | $291.2 M | $1.07 B |
| [Tetouan](Tetouan/README.md) | 500,000 | 262 | $1.61 B | $326.8 M | $1.28 B |
| [Safi](Safi/README.md) | 350,000 | 150 | $769.5 M | $162.3 M | $607.1 M |
| [Beni Mellal](Beni-Mellal/README.md) | 300,000 | 82 | $546.6 M | $104.4 M | $442.2 M |
| [Khouribga](Khouribga/README.md) | 250,000 | 63 | $433.7 M | $84.3 M | $349.5 M |
| [Nador](Nador/README.md) | 250,000 | 117 | $792.2 M | $151.2 M | $641.0 M |

## Local Basis And Regeneration

Country finance parameters use `MA` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

| City | Current lines | Added residential lines | Original station circles | Current station circles |
| --- | ---: | ---: | ---: | ---: |
| [Agadir](Agadir/README.md) | 10 | 7 | 46.8% | 77.7% |
| [Beni Mellal](Beni-Mellal/README.md) | 5 | 2 | 59.0% | 79.8% |
| [Fez](Fez/README.md) | 9 | 5 | 46.0% | 80.5% |
| [Kenitra](Kenitra/README.md) | 7 | 4 | 50.8% | 85.1% |
| [Khouribga](Khouribga/README.md) | 5 | 2 | 49.3% | 79.8% |
| [Marrakech](Marrakech/README.md) | 15 | 9 | 41.2% | 79.7% |
| [Meknes](Meknes/README.md) | 9 | 6 | 38.9% | 79.7% |
| [Nador](Nador/README.md) | 6 | 3 | 47.2% | 82.0% |
| [Oujda](Oujda/README.md) | 5 | 2 | 51.7% | 77.3% |
| [Safi](Safi/README.md) | 5 | 2 | 67.8% | 84.0% |
| [Tangier](Tangier/README.md) | 8 | 3 | 57.5% | 78.0% |
| [Tetouan](Tetouan/README.md) | 8 | 5 | 40.4% | 81.2% |

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
