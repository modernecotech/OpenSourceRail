# Bangladesh National OpenSourceRail Strategy

This page contains only Bangladesh-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$41.08 B (88.3%) of external capital** and **$51.49 B of external interest**. Capital plus saved interest totals **$92.57 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 10 |
| Represented population | 13,550,000 |
| Trainsets / vehicle modules | 2,956 / 11,750 |
| City infrastructure and fleet CAPEX | $24.86 B |
| Shared national factory | $927.4 M |
| Factory sizing basis | 4,350 modules for Chittagong, then reused nationally |
| **Total national programme** | **$25.85 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $5.46 B (21.1%) |
| Domestic / local capital | $20.40 B (78.9%) |
| Annual external capital draw | $779.5 M / yr |
| Annual local capital draw | $2.91 B / yr |
| Annual public construction commitment | $2.22 B / yr for 7 years |
| Annual post-grace debt service | $1.81 B / yr |
| Default foreign-turnkey external capital | $46.54 B |
| External capital saved | $41.08 B |
| Capital + lifetime external interest saved | $92.57 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $12.97 B | $1.95 B | $11.03 B |
| Stations | $3.92 B | $784.8 M | $3.14 B |
| Depots | $1.27 B | $316.3 M | $949.0 M |
| Rolling stock | $3.38 B | $1.18 B | $2.20 B |
| Dedicated solar plants | $1.57 B | $708.7 M | $866.2 M |
| Residual train control | $67.0 M | $33.5 M | $33.5 M |
| Charging microgrids | $149.9 M | $60.0 M | $90.0 M |
| EPC / project services | $1.59 B | $238.2 M | $1.35 B |
| Shared national trainset factory | $927.4 M | $185.5 M | $741.9 M |
| **Total** | **$25.85 B** | **$5.46 B** | **$20.40 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital | Lines | Added lines | Original circles | Current circles |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| [Chittagong](Chittagong/README.md) | 5,200,000 | 725 | $7.79 B | $1.74 B | $6.05 B | 12 | 4 | 46.6% | 48.1% |
| [Khulna](Khulna/README.md) | 1,500,000 | 313 | $3.74 B | $753.3 M | $2.99 B | 9 | 3 | 51.8% | 41.9% |
| [Gazipur](Gazipur/README.md) | 1,400,000 | 394 | $4.40 B | $908.6 M | $3.49 B | 9 | 3 | 29.1% | 30.3% |
| [Narayanganj](Narayanganj/README.md) | 950,000 | 283 | $1.59 B | $333.4 M | $1.26 B | 5 | 2 | 34.2% | 34.2% |
| [Rajshahi](Rajshahi/README.md) | 950,000 | 203 | $1.13 B | $240.8 M | $893.0 M | 4 | 1 | 36.1% | 37.8% |
| [Sylhet](Sylhet/README.md) | 900,000 | 192 | $1.12 B | $232.1 M | $889.6 M | 4 | 1 | 25.1% | 33.6% |
| [Rangpur](Rangpur/README.md) | 800,000 | 164 | $916.6 M | $191.4 M | $725.1 M | 5 | 2 | 22.4% | 25.2% |
| [Mymensingh](Mymensingh/README.md) | 700,000 | 164 | $1.13 B | $227.1 M | $907.0 M | 4 | 1 | 18.8% | 21.6% |
| [Comilla](Comilla/README.md) | 600,000 | 277 | $1.63 B | $340.9 M | $1.29 B | 5 | 2 | 28.7% | 33.1% |
| [Barisal](Barisal/README.md) | 550,000 | 241 | $1.41 B | $293.3 M | $1.11 B | 5 | 2 | 39.6% | 52.4% |

## Local Basis And Regeneration

Country finance parameters use `BD` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
