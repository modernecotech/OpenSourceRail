# Madagascar National OpenSourceRail Strategy

This page contains only Madagascar-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$21.57 B (87.5%) of external capital** and **$27.87 B of external interest**. Capital plus saved interest totals **$49.44 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 3,058,000 |
| Trainsets / vehicle modules | 1,399 / 8,394 |
| City infrastructure and fleet CAPEX | $13.16 B |
| Shared national factory | $503.6 M |
| Factory sizing basis | 8,394 modules for Antananarivo, then reused nationally |
| **Total national programme** | **$13.70 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $3.09 B (22.5%) |
| Domestic / local capital | $10.61 B (77.5%) |
| Annual external capital draw | $308.8 M / yr |
| Annual local capital draw | $1.06 B / yr |
| Annual public construction commitment | $1.29 B / yr for 10 years |
| Annual post-grace debt service | $1.17 B / yr |
| Default foreign-turnkey external capital | $24.66 B |
| External capital saved | $21.57 B |
| Capital + lifetime external interest saved | $49.44 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $5.36 B | $804.5 M | $4.56 B |
| Stations | $2.73 B | $547.0 M | $2.19 B |
| Depots | $829.9 M | $207.5 M | $622.4 M |
| Rolling stock | $2.35 B | $822.6 M | $1.53 B |
| Dedicated solar plants | $899.1 M | $404.6 M | $494.5 M |
| Residual train control | $27.2 M | $13.6 M | $13.6 M |
| Charging microgrids | $154.1 M | $61.6 M | $92.5 M |
| EPC / project services | $837.4 M | $125.6 M | $711.8 M |
| Shared national trainset factory | $503.6 M | $100.7 M | $402.9 M |
| **Total** | **$13.70 B** | **$3.09 B** | **$10.61 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Antananarivo](Antananarivo/README.md) | 3,058,000 | 1,399 | $13.16 B | $2.98 B | $10.18 B |

## Local Basis And Regeneration

Country finance parameters use `MG` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

| City | Current lines | Added residential lines | Original station circles | Current station circles |
| --- | ---: | ---: | ---: | ---: |
| [Antananarivo](Antananarivo/README.md) | 40 | 31 | 35.7% | 81.0% |

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
