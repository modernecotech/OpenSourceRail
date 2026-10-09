# Somalia National OpenSourceRail Strategy

This page contains only Somalia-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$5.80 B (88.7%) of external capital** and **$7.49 B of external interest**. Capital plus saved interest totals **$13.29 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 2,610,000 |
| Trainsets / vehicle modules | 296 / 1,184 |
| City infrastructure and fleet CAPEX | $2.71 B |
| Shared national factory | $857.4 M |
| Factory sizing basis | 1,184 modules for Mogadishu, then reused nationally |
| **Total national programme** | **$3.63 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $737.1 M (20.3%) |
| Domestic / local capital | $2.89 B (79.7%) |
| Annual external capital draw | $73.7 M / yr |
| Annual local capital draw | $289.3 M / yr |
| Annual public construction commitment | $438.2 M / yr for 10 years |
| Annual post-grace debt service | $397.8 M / yr |
| Default foreign-turnkey external capital | $6.53 B |
| External capital saved | $5.80 B |
| Capital + lifetime external interest saved | $13.29 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $1.34 B | $201.3 M | $1.14 B |
| Stations | $545.5 M | $109.1 M | $436.4 M |
| Depots | $197.8 M | $49.4 M | $148.3 M |
| Rolling stock | $331.5 M | $116.0 M | $215.5 M |
| Dedicated solar plants | $88.5 M | $39.8 M | $48.7 M |
| Residual train control | $7.8 M | $3.9 M | $3.9 M |
| Charging microgrids | $28.1 M | $11.2 M | $16.9 M |
| EPC / project services | $231.7 M | $34.8 M | $196.9 M |
| Shared national trainset factory | $857.4 M | $171.5 M | $685.9 M |
| **Total** | **$3.63 B** | **$737.1 M** | **$2.89 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Mogadishu](Mogadishu/README.md) | 2,610,000 | 296 | $2.71 B | $556.6 M | $2.16 B |

## Local Basis And Regeneration

Country finance parameters use `SO` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

| City | Current lines | Added residential lines | Original station circles | Current station circles |
| --- | ---: | ---: | ---: | ---: |
| [Mogadishu](Mogadishu/README.md) | 12 | 8 | 37.7% | 78.0% |

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
