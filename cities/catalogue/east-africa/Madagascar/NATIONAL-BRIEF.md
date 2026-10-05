# Madagascar National OpenSourceRail Strategy

This page contains only Madagascar-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$9.72 B (87.9%) of external capital** and **$12.56 B of external interest**. Capital plus saved interest totals **$22.28 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 3,058,000 |
| Trainsets / vehicle modules | 476 / 2,856 |
| City infrastructure and fleet CAPEX | $5.60 B |
| Shared national factory | $504.6 M |
| Factory sizing basis | 2,856 modules for Antananarivo, then reused nationally |
| **Total national programme** | **$6.14 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.34 B (21.8%) |
| Domestic / local capital | $4.81 B (78.2%) |
| Annual external capital draw | $133.8 M / yr |
| Annual local capital draw | $480.5 M / yr |
| Annual public construction commitment | $579.2 M / yr for 10 years |
| Annual post-grace debt service | $524.3 M / yr |
| Default foreign-turnkey external capital | $11.06 B |
| External capital saved | $9.72 B |
| Capital + lifetime external interest saved | $22.28 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $2.97 B | $445.8 M | $2.53 B |
| Stations | $686.0 M | $137.2 M | $548.8 M |
| Depots | $227.7 M | $56.9 M | $170.8 M |
| Rolling stock | $799.7 M | $279.9 M | $519.8 M |
| Dedicated solar plants | $529.1 M | $238.1 M | $291.0 M |
| Residual train control | $14.7 M | $7.4 M | $7.4 M |
| Charging microgrids | $42.6 M | $17.0 M | $25.6 M |
| EPC / project services | $367.3 M | $55.1 M | $312.2 M |
| Shared national trainset factory | $504.6 M | $100.9 M | $403.7 M |
| **Total** | **$6.14 B** | **$1.34 B** | **$4.81 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Antananarivo](Antananarivo/README.md) | 3,058,000 | 476 | $5.60 B | $1.23 B | $4.37 B |

## Local Basis And Regeneration

Country finance parameters use `MG` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
