# Laos National OpenSourceRail Strategy

This page contains only Laos-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$5.26 B (88.5%) of external capital** and **$6.59 B of external interest**. Capital plus saved interest totals **$11.85 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 948,000 |
| Trainsets / vehicle modules | 442 / 1,326 |
| City infrastructure and fleet CAPEX | $2.38 B |
| Shared national factory | $863.1 M |
| Factory sizing basis | 1,326 modules for Vientiane, then reused nationally |
| **Total national programme** | **$3.30 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $683.3 M (20.7%) |
| Domestic / local capital | $2.62 B (79.3%) |
| Annual external capital draw | $97.6 M / yr |
| Annual local capital draw | $374.0 M / yr |
| Annual public construction commitment | $325.5 M / yr for 7 years |
| Annual post-grace debt service | $268.5 M / yr |
| Default foreign-turnkey external capital | $5.94 B |
| External capital saved | $5.26 B |
| Capital + lifetime external interest saved | $11.85 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $1.10 B | $165.4 M | $937.5 M |
| Stations | $409.1 M | $81.8 M | $327.3 M |
| Depots | $249.1 M | $62.3 M | $186.8 M |
| Rolling stock | $397.8 M | $139.2 M | $258.6 M |
| Dedicated solar plants | $52.8 M | $23.8 M | $29.0 M |
| Residual train control | $6.2 M | $3.1 M | $3.1 M |
| Charging microgrids | $8.0 M | $3.2 M | $4.8 M |
| EPC / project services | $212.5 M | $31.9 M | $180.7 M |
| Shared national trainset factory | $863.1 M | $172.6 M | $690.5 M |
| **Total** | **$3.30 B** | **$683.3 M** | **$2.62 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Vientiane](Vientiane/README.md) | 948,000 | 442 | $2.38 B | $501.6 M | $1.88 B |

## Local Basis And Regeneration

Country finance parameters use `LA` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

| City | Current lines | Added residential lines | Original station circles | Current station circles |
| --- | ---: | ---: | ---: | ---: |
| [Vientiane](Vientiane/README.md) | 16 | 13 | 26.4% | 70.5% |

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
