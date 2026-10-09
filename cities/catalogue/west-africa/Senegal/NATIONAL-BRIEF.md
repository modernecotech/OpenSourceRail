# Senegal National OpenSourceRail Strategy

This page contains only Senegal-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$9.08 B (87.7%) of external capital** and **$11.38 B of external interest**. Capital plus saved interest totals **$20.46 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 4,030,000 |
| Trainsets / vehicle modules | 583 / 3,498 |
| City infrastructure and fleet CAPEX | $5.40 B |
| Shared national factory | $326.9 M |
| Factory sizing basis | 3,498 modules for Dakar, then reused nationally |
| **Total national programme** | **$5.75 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.27 B (22.1%) |
| Domestic / local capital | $4.48 B (77.9%) |
| Annual external capital draw | $181.6 M / yr |
| Annual local capital draw | $640.0 M / yr |
| Annual public construction commitment | $489.8 M / yr for 7 years |
| Annual post-grace debt service | $401.4 M / yr |
| Default foreign-turnkey external capital | $10.35 B |
| External capital saved | $9.08 B |
| Capital + lifetime external interest saved | $20.46 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $2.31 B | $346.0 M | $1.96 B |
| Stations | $1.09 B | $217.6 M | $870.4 M |
| Depots | $316.5 M | $79.1 M | $237.3 M |
| Rolling stock | $979.4 M | $342.8 M | $636.6 M |
| Dedicated solar plants | $293.3 M | $132.0 M | $161.3 M |
| Residual train control | $13.3 M | $6.7 M | $6.7 M |
| Charging microgrids | $69.8 M | $27.9 M | $41.9 M |
| EPC / project services | $357.0 M | $53.6 M | $303.5 M |
| Shared national trainset factory | $326.9 M | $65.4 M | $261.5 M |
| **Total** | **$5.75 B** | **$1.27 B** | **$4.48 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Dakar](Dakar/README.md) | 4,030,000 | 583 | $5.40 B | $1.20 B | $4.20 B |

## Local Basis And Regeneration

Country finance parameters use `SN` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

| City | Current lines | Added residential lines | Original station circles | Current station circles |
| --- | ---: | ---: | ---: | ---: |
| [Dakar](Dakar/README.md) | 14 | 8 | 56.0% | 84.9% |

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
