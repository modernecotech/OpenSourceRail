# Laos National OpenSourceRail Strategy

This page contains only Laos-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$2.51 B (88.6%) of external capital** and **$3.15 B of external interest**. Capital plus saved interest totals **$5.66 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 948,000 |
| Trainsets / vehicle modules | 186 / 558 |
| City infrastructure and fleet CAPEX | $983.6 M |
| Shared national factory | $554.0 M |
| Factory sizing basis | 558 modules for Vientiane, then reused nationally |
| **Total national programme** | **$1.58 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $324.8 M (20.6%) |
| Domestic / local capital | $1.25 B (79.4%) |
| Annual external capital draw | $46.4 M / yr |
| Annual local capital draw | $178.8 M / yr |
| Annual public construction commitment | $155.5 M / yr for 7 years |
| Annual post-grace debt service | $128.3 M / yr |
| Default foreign-turnkey external capital | $2.84 B |
| External capital saved | $2.51 B |
| Capital + lifetime external interest saved | $5.66 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $559.5 M | $83.9 M | $475.5 M |
| Stations | $76.1 M | $15.2 M | $60.9 M |
| Depots | $62.9 M | $15.7 M | $47.1 M |
| Rolling stock | $167.4 M | $58.6 M | $108.8 M |
| Dedicated solar plants | $51.6 M | $23.2 M | $28.4 M |
| Residual train control | $3.0 M | $1.5 M | $1.5 M |
| Charging microgrids | $2.1 M | $860 k | $1.3 M |
| EPC / project services | $99.8 M | $15.0 M | $84.8 M |
| Shared national trainset factory | $554.0 M | $110.8 M | $443.2 M |
| **Total** | **$1.58 B** | **$324.8 M** | **$1.25 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Vientiane](Vientiane/README.md) | 948,000 | 186 | $983.6 M | $208.2 M | $775.4 M |

## Local Basis And Regeneration

Country finance parameters use `LA` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
