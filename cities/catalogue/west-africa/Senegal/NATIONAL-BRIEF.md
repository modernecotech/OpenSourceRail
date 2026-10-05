# Senegal National OpenSourceRail Strategy

This page contains only Senegal-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$6.51 B (88.2%) of external capital** and **$8.17 B of external interest**. Capital plus saved interest totals **$14.68 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 4,030,000 |
| Trainsets / vehicle modules | 284 / 1,704 |
| City infrastructure and fleet CAPEX | $3.08 B |
| Shared national factory | $960.1 M |
| Factory sizing basis | 1,704 modules for Dakar, then reused nationally |
| **Total national programme** | **$4.10 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $869.8 M (21.2%) |
| Domestic / local capital | $3.23 B (78.8%) |
| Annual external capital draw | $124.3 M / yr |
| Annual local capital draw | $461.8 M / yr |
| Annual public construction commitment | $351.3 M / yr for 7 years |
| Annual post-grace debt service | $286.9 M / yr |
| Default foreign-turnkey external capital | $7.38 B |
| External capital saved | $6.51 B |
| Capital + lifetime external interest saved | $14.68 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $1.68 B | $251.9 M | $1.43 B |
| Stations | $317.8 M | $63.6 M | $254.2 M |
| Depots | $142.6 M | $35.6 M | $106.9 M |
| Rolling stock | $477.1 M | $167.0 M | $310.1 M |
| Dedicated solar plants | $235.9 M | $106.1 M | $129.7 M |
| Residual train control | $9.7 M | $4.8 M | $4.8 M |
| Charging microgrids | $27.0 M | $10.8 M | $16.2 M |
| EPC / project services | $253.0 M | $37.9 M | $215.0 M |
| Shared national trainset factory | $960.1 M | $192.0 M | $768.1 M |
| **Total** | **$4.10 B** | **$869.8 M** | **$3.23 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Dakar](Dakar/README.md) | 4,030,000 | 284 | $3.08 B | $667.7 M | $2.41 B |

## Local Basis And Regeneration

Country finance parameters use `SN` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
