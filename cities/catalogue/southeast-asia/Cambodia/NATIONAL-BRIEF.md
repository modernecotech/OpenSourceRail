# Cambodia National OpenSourceRail Strategy

This page contains only Cambodia-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$16.57 B (90.3%) of external capital** and **$20.77 B of external interest**. Capital plus saved interest totals **$37.34 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 2,281,000 |
| Trainsets / vehicle modules | 374 / 1,496 |
| City infrastructure and fleet CAPEX | $9.62 B |
| Shared national factory | $534.3 M |
| Factory sizing basis | 1,496 modules for Phnom Penh, then reused nationally |
| **Total national programme** | **$10.20 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.78 B (17.5%) |
| Domestic / local capital | $8.41 B (82.5%) |
| Annual external capital draw | $254.7 M / yr |
| Annual local capital draw | $1.20 B / yr |
| Annual public construction commitment | $859.0 M / yr for 7 years |
| Annual post-grace debt service | $689.3 M / yr |
| Default foreign-turnkey external capital | $18.35 B |
| External capital saved | $16.57 B |
| Capital + lifetime external interest saved | $37.34 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $7.43 B | $1.11 B | $6.32 B |
| Stations | $703.5 M | $140.7 M | $562.8 M |
| Depots | $142.0 M | $35.5 M | $106.5 M |
| Rolling stock | $418.9 M | $146.6 M | $272.3 M |
| Dedicated solar plants | $272.8 M | $122.8 M | $150.1 M |
| Residual train control | $12.2 M | $6.1 M | $6.1 M |
| Charging microgrids | $31.4 M | $12.5 M | $18.8 M |
| EPC / project services | $649.2 M | $97.4 M | $551.8 M |
| Shared national trainset factory | $534.3 M | $106.9 M | $427.5 M |
| **Total** | **$10.20 B** | **$1.78 B** | **$8.41 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Phnom Penh](Phnom-Penh/README.md) | 2,281,000 | 374 | $9.62 B | $1.67 B | $7.95 B |

## Local Basis And Regeneration

Country finance parameters use `KH` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
