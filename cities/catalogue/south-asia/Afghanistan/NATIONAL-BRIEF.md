# Afghanistan National OpenSourceRail Strategy

This page contains only Afghanistan-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$17.39 B (88.1%) of external capital** and **$22.46 B of external interest**. Capital plus saved interest totals **$39.85 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 5 |
| Represented population | 7,051,000 |
| Trainsets / vehicle modules | 1,388 / 6,036 |
| City infrastructure and fleet CAPEX | $10.22 B |
| Shared national factory | $696.0 M |
| Factory sizing basis | 3,744 modules for Kabul, then reused nationally |
| **Total national programme** | **$10.97 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $2.35 B (21.4%) |
| Domestic / local capital | $8.62 B (78.6%) |
| Annual external capital draw | $235.1 M / yr |
| Annual local capital draw | $861.5 M / yr |
| Annual public construction commitment | $1.52 B / yr for 10 years |
| Annual post-grace debt service | $1.39 B / yr |
| Default foreign-turnkey external capital | $19.74 B |
| External capital saved | $17.39 B |
| Capital + lifetime external interest saved | $39.85 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $4.60 B | $690.3 M | $3.91 B |
| Stations | $2.09 B | $417.1 M | $1.67 B |
| Depots | $620.3 M | $155.1 M | $465.2 M |
| Rolling stock | $1.74 B | $607.6 M | $1.13 B |
| Dedicated solar plants | $418.5 M | $188.3 M | $230.2 M |
| Residual train control | $25.1 M | $12.5 M | $12.5 M |
| Charging microgrids | $92.2 M | $36.9 M | $55.4 M |
| EPC / project services | $690.0 M | $103.5 M | $586.5 M |
| Shared national trainset factory | $696.0 M | $139.2 M | $556.8 M |
| **Total** | **$10.97 B** | **$2.35 B** | **$8.62 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital | Lines | Added lines | Original circles | Current circles |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| [Kabul](Kabul/README.md) | 4,601,000 | 624 | $6.02 B | $1.33 B | $4.68 B | 11 | 4 | 40.8% | 40.7% |
| [Herat](Herat/README.md) | 800,000 | 153 | $822.5 M | $170.0 M | $652.5 M | 4 | 1 | 18.8% | 19.9% |
| [Kandahar](Kandahar/README.md) | 700,000 | 204 | $1.10 B | $229.1 M | $874.1 M | 5 | 2 | 27.0% | 42.5% |
| [Mazar E Sharif](Mazar-E-Sharif/README.md) | 600,000 | 237 | $1.29 B | $269.7 M | $1.02 B | 5 | 2 | 44.3% | 57.8% |
| [Jalalabad Af](Jalalabad-Af/README.md) | 350,000 | 170 | $984.2 M | $200.8 M | $783.5 M | 5 | 2 | 31.3% | 36.8% |

## Local Basis And Regeneration

Country finance parameters use `AF` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
