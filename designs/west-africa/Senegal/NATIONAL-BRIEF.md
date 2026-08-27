# Senegal National OpenSourceRail Strategy

This page contains only Senegal-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$3.55 B (85.9%) of external capital** and **$4.45 B of external interest**. Capital plus saved interest totals **$8.00 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 4,030,000 |
| Trainsets / vehicle modules | 330 / 1,980 |
| City infrastructure and fleet CAPEX | $2.17 B |
| Shared national factory | $118.8 M |
| Factory sizing basis | 1,980 modules for Dakar, then reused nationally |
| **Total national programme** | **$2.30 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $585.1 M (25.5%) |
| Domestic / local capital | $1.71 B (74.5%) |
| Annual external capital draw | $83.6 M / yr |
| Annual local capital draw | $244.7 M / yr |
| Annual public construction commitment | $191.7 M / yr for 7 years |
| Annual post-grace debt service | $159.3 M / yr |
| Default foreign-turnkey external capital | $4.14 B |
| External capital saved | $3.55 B |
| Capital + lifetime external interest saved | $8.00 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $718.1 M | $107.7 M | $610.4 M |
| Stations | $425.4 M | $85.1 M | $340.3 M |
| Depots | $8.0 M | $2.0 M | $6.0 M |
| Rolling stock | $554.4 M | $194.0 M | $360.4 M |
| Dedicated solar plants | $297.2 M | $133.7 M | $163.5 M |
| Residual train control | $11.1 M | $5.6 M | $5.6 M |
| Charging microgrids | $33.9 M | $13.6 M | $20.3 M |
| EPC / project services | $130.9 M | $19.6 M | $111.2 M |
| Shared national trainset factory | $118.8 M | $23.8 M | $95.0 M |
| **Total** | **$2.30 B** | **$585.1 M** | **$1.71 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Dakar](Dakar/README.md) | 4,030,000 | 330 | $2.17 B | $560.1 M | $1.61 B |

## Local Basis And Regeneration

Country finance parameters use `SN` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 scripts/generate-national-briefs.py
```
