# Laos National OpenSourceRail Strategy

This page contains only Laos-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$2.61 B (88.5%) of external capital** and **$3.28 B of external interest**. Capital plus saved interest totals **$5.89 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 948,000 |
| Trainsets / vehicle modules | 195 / 585 |
| City infrastructure and fleet CAPEX | $1.01 B |
| Shared national factory | $584.4 M |
| Factory sizing basis | 585 modules for Vientiane, then reused nationally |
| **Total national programme** | **$1.64 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $338.5 M (20.6%) |
| Domestic / local capital | $1.30 B (79.4%) |
| Annual external capital draw | $48.4 M / yr |
| Annual local capital draw | $185.9 M / yr |
| Annual public construction commitment | $161.7 M / yr for 7 years |
| Annual post-grace debt service | $133.4 M / yr |
| Default foreign-turnkey external capital | $2.95 B |
| External capital saved | $2.61 B |
| Capital + lifetime external interest saved | $5.89 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $566.8 M | $85.0 M | $481.8 M |
| Stations | $87.6 M | $17.5 M | $70.1 M |
| Depots | $63.2 M | $15.8 M | $47.4 M |
| Rolling stock | $175.5 M | $61.4 M | $114.1 M |
| Dedicated solar plants | $53.0 M | $23.8 M | $29.1 M |
| Residual train control | $3.1 M | $1.6 M | $1.6 M |
| Charging microgrids | $2.2 M | $900 k | $1.4 M |
| EPC / project services | $103.8 M | $15.6 M | $88.2 M |
| Shared national trainset factory | $584.4 M | $116.9 M | $467.5 M |
| **Total** | **$1.64 B** | **$338.5 M** | **$1.30 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Vientiane](Vientiane/README.md) | 948,000 | 195 | $1.01 B | $215.5 M | $798.8 M |

## Local Basis And Regeneration

Country finance parameters use `LA` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
