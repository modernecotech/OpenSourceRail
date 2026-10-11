# South Africa National OpenSourceRail Strategy

This page contains only South Africa-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$35.86 B (87.6%) of external capital** and **$44.09 B of external interest**. Capital plus saved interest totals **$79.95 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 5 |
| Represented population | 6,200,000 |
| Trainsets / vehicle modules | 2,778 / 13,607 |
| City infrastructure and fleet CAPEX | $21.82 B |
| Shared national factory | $863.1 M |
| Factory sizing basis | 10,770 modules for Durban, then reused nationally |
| **Total national programme** | **$22.74 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $5.08 B (22.3%) |
| Domestic / local capital | $17.67 B (77.7%) |
| Annual external capital draw | $1.02 B / yr |
| Annual local capital draw | $3.53 B / yr |
| Annual public construction commitment | $2.42 B / yr for 5 years |
| Annual post-grace debt service | $1.82 B / yr |
| Default foreign-turnkey external capital | $40.94 B |
| External capital saved | $35.86 B |
| Capital + lifetime external interest saved | $79.95 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $9.11 B | $1.37 B | $7.75 B |
| Stations | $4.32 B | $864.4 M | $3.46 B |
| Depots | $1.57 B | $392.1 M | $1.18 B |
| Rolling stock | $3.86 B | $1.35 B | $2.51 B |
| Dedicated solar plants | $1.34 B | $604.7 M | $739.0 M |
| Residual train control | $50.3 M | $25.2 M | $25.2 M |
| Charging microgrids | $217.7 M | $87.1 M | $130.6 M |
| EPC / project services | $1.40 B | $210.0 M | $1.19 B |
| Shared national trainset factory | $863.1 M | $172.6 M | $690.5 M |
| **Total** | **$22.74 B** | **$5.08 B** | **$17.67 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Durban](Durban/README.md) | 3,900,000 | 1,795 | $16.42 B | $3.76 B | $12.65 B |
| [East London Za](East-London-Za/README.md) | 800,000 | 316 | $1.72 B | $367.0 M | $1.35 B |
| [Bloemfontein](Bloemfontein/README.md) | 600,000 | 287 | $1.47 B | $317.7 M | $1.15 B |
| [Polokwane](Polokwane/README.md) | 600,000 | 268 | $1.41 B | $293.3 M | $1.12 B |
| [Nelspruit](Nelspruit/README.md) | 300,000 | 112 | $805.9 M | $152.5 M | $653.5 M |

## Local Basis And Regeneration

Country finance parameters use `ZA` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

| City | Current lines | Added residential lines | Original station circles | Current station circles |
| --- | ---: | ---: | ---: | ---: |
| [Bloemfontein](Bloemfontein/README.md) | 9 | 6 | 39.1% | 79.1% |
| [Durban](Durban/README.md) | 47 | 38 | 28.1% | 82.8% |
| [East London Za](East-London-Za/README.md) | 10 | 7 | 34.3% | 84.0% |
| [Nelspruit](Nelspruit/README.md) | 6 | 3 | 40.1% | 78.9% |
| [Polokwane](Polokwane/README.md) | 11 | 8 | 23.0% | 76.7% |

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
