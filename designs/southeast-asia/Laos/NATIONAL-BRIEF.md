# Laos National OpenSourceRail Strategy

This page contains only Laos-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$954.4 M (86.2%) of external capital** and **$1.20 B of external interest**. Capital plus saved interest totals **$2.15 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 948,000 |
| Trainsets / vehicle modules | 155 / 465 |
| City infrastructure and fleet CAPEX | $585.0 M |
| Shared national factory | $27.9 M |
| Factory sizing basis | 465 modules for Vientiane, then reused nationally |
| **Total national programme** | **$614.8 M** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $152.3 M (24.8%) |
| Domestic / local capital | $462.6 M (75.2%) |
| Annual external capital draw | $21.8 M / yr |
| Annual local capital draw | $66.1 M / yr |
| Annual public construction commitment | $58.9 M / yr for 7 years |
| Annual post-grace debt service | $49.3 M / yr |
| Default foreign-turnkey external capital | $1.11 B |
| External capital saved | $954.4 M |
| Capital + lifetime external interest saved | $2.15 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $210.5 M | $31.6 M | $178.9 M |
| Stations | $112.6 M | $22.5 M | $90.1 M |
| Depots | $8.0 M | $2.0 M | $6.0 M |
| Rolling stock | $139.5 M | $48.8 M | $90.7 M |
| Dedicated solar plants | $74.4 M | $33.5 M | $40.9 M |
| Residual train control | $3.7 M | $1.9 M | $1.9 M |
| Charging microgrids | $2.8 M | $1.1 M | $1.7 M |
| EPC / project services | $35.4 M | $5.3 M | $30.1 M |
| Shared national trainset factory | $27.9 M | $5.6 M | $22.3 M |
| **Total** | **$614.8 M** | **$152.3 M** | **$462.6 M** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Vientiane](Vientiane/README.md) | 948,000 | 155 | $585.0 M | $146.4 M | $438.6 M |

## Local Basis And Regeneration

Country finance parameters use `LA` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 scripts/generate-national-briefs.py
```
