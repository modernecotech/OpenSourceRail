# Madagascar National OpenSourceRail Strategy

This page contains only Madagascar-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$9.13 B (87.9%) of external capital** and **$11.79 B of external interest**. Capital plus saved interest totals **$20.91 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 3,058,000 |
| Trainsets / vehicle modules | 449 / 2,694 |
| City infrastructure and fleet CAPEX | $5.20 B |
| Shared national factory | $529.8 M |
| Factory sizing basis | 2,694 modules for Antananarivo, then reused nationally |
| **Total national programme** | **$5.77 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.26 B (21.8%) |
| Domestic / local capital | $4.51 B (78.2%) |
| Annual external capital draw | $125.8 M / yr |
| Annual local capital draw | $451.1 M / yr |
| Annual public construction commitment | $543.8 M / yr for 10 years |
| Annual post-grace debt service | $492.3 M / yr |
| Default foreign-turnkey external capital | $10.38 B |
| External capital saved | $9.13 B |
| Capital + lifetime external interest saved | $20.91 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $2.93 B | $439.4 M | $2.49 B |
| Stations | $415.4 M | $83.1 M | $332.3 M |
| Depots | $221.1 M | $55.3 M | $165.8 M |
| Rolling stock | $754.3 M | $264.0 M | $490.3 M |
| Dedicated solar plants | $531.2 M | $239.0 M | $292.2 M |
| Residual train control | $14.6 M | $7.3 M | $7.3 M |
| Charging microgrids | $30.2 M | $12.1 M | $18.1 M |
| EPC / project services | $342.6 M | $51.4 M | $291.2 M |
| Shared national trainset factory | $529.8 M | $106.0 M | $423.9 M |
| **Total** | **$5.77 B** | **$1.26 B** | **$4.51 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Antananarivo](Antananarivo/README.md) | 3,058,000 | 449 | $5.20 B | $1.15 B | $4.06 B |

## Local Basis And Regeneration

Country finance parameters use `MG` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
