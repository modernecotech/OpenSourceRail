# Palestine National OpenSourceRail Strategy

This page contains only Palestine-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$4.50 B (88.3%) of external capital** and **$5.64 B of external interest**. Capital plus saved interest totals **$10.13 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 3 |
| Represented population | 1,850,000 |
| Trainsets / vehicle modules | 442 / 1,326 |
| City infrastructure and fleet CAPEX | $2.20 B |
| Shared national factory | $584.4 M |
| Factory sizing basis | 585 modules for Nablus, then reused nationally |
| **Total national programme** | **$2.83 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $593.1 M (21.0%) |
| Domestic / local capital | $2.23 B (79.0%) |
| Annual external capital draw | $84.7 M / yr |
| Annual local capital draw | $319.1 M / yr |
| Annual public construction commitment | $242.4 M / yr for 7 years |
| Annual post-grace debt service | $197.8 M / yr |
| Default foreign-turnkey external capital | $5.09 B |
| External capital saved | $4.50 B |
| Capital + lifetime external interest saved | $10.13 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $1.15 B | $171.8 M | $973.5 M |
| Stations | $248.7 M | $49.7 M | $199.0 M |
| Depots | $169.1 M | $42.3 M | $126.8 M |
| Rolling stock | $397.8 M | $139.2 M | $258.6 M |
| Dedicated solar plants | $90.7 M | $40.8 M | $49.9 M |
| Residual train control | $7.1 M | $3.5 M | $3.5 M |
| Charging microgrids | $5.0 M | $2.0 M | $3.0 M |
| EPC / project services | $179.0 M | $26.9 M | $152.2 M |
| Shared national trainset factory | $584.4 M | $116.9 M | $467.5 M |
| **Total** | **$2.83 B** | **$593.1 M** | **$2.23 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Hebron](Hebron/README.md) | 800,000 | 155 | $818.2 M | $172.2 M | $646.0 M |
| [Gaza City](Gaza-City/README.md) | 600,000 | 92 | $472.6 M | $100.2 M | $372.4 M |
| [Nablus](Nablus/README.md) | 450,000 | 195 | $911.0 M | $197.7 M | $713.3 M |

## Local Basis And Regeneration

Country finance parameters use `PS` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
