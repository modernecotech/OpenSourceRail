# Cambodia National OpenSourceRail Strategy

This page contains only Cambodia-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$9.65 B (88.7%) of external capital** and **$12.09 B of external interest**. Capital plus saved interest totals **$21.74 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 2,281,000 |
| Trainsets / vehicle modules | 515 / 2,060 |
| City infrastructure and fleet CAPEX | $5.67 B |
| Shared national factory | $351.7 M |
| Factory sizing basis | 2,060 modules for Phnom Penh, then reused nationally |
| **Total national programme** | **$6.04 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.23 B (20.3%) |
| Domestic / local capital | $4.81 B (79.7%) |
| Annual external capital draw | $175.4 M / yr |
| Annual local capital draw | $687.7 M / yr |
| Annual public construction commitment | $500.9 M / yr for 7 years |
| Annual post-grace debt service | $406.6 M / yr |
| Default foreign-turnkey external capital | $10.87 B |
| External capital saved | $9.65 B |
| Capital + lifetime external interest saved | $21.74 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $3.08 B | $462.4 M | $2.62 B |
| Stations | $1.07 B | $213.1 M | $852.4 M |
| Depots | $203.2 M | $50.8 M | $152.4 M |
| Rolling stock | $576.8 M | $201.9 M | $374.9 M |
| Dedicated solar plants | $329.1 M | $148.1 M | $181.0 M |
| Residual train control | $14.9 M | $7.5 M | $7.5 M |
| Charging microgrids | $43.7 M | $17.5 M | $26.2 M |
| EPC / project services | $373.7 M | $56.1 M | $317.6 M |
| Shared national trainset factory | $351.7 M | $70.3 M | $281.4 M |
| **Total** | **$6.04 B** | **$1.23 B** | **$4.81 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital | Lines | Added lines | Original circles | Current circles |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| [Phnom Penh](Phnom-Penh/README.md) | 2,281,000 | 515 | $5.67 B | $1.15 B | $4.51 B | 9 | 3 | 34.2% | 44.4% |

## Local Basis And Regeneration

Country finance parameters use `KH` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
