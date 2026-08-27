# France National OpenSourceRail Strategy

This page contains only France-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$3.60 B (86.2%) of external capital** and **$4.35 B of external interest**. Capital plus saved interest totals **$7.95 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 1,436,354 |
| Trainsets / vehicle modules | 347 / 1,388 |
| City infrastructure and fleet CAPEX | $2.23 B |
| Shared national factory | $83.3 M |
| Factory sizing basis | 1,388 modules for Lyon, then reused nationally |
| **Total national programme** | **$2.32 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $578.7 M (24.9%) |
| Domestic / local capital | $1.74 B (75.1%) |
| Annual external capital draw | $192.9 M / yr |
| Annual local capital draw | $581.5 M / yr |
| Annual public construction commitment | $184.2 M / yr for 3 years |
| Annual post-grace debt service | $95.4 M / yr |
| Default foreign-turnkey external capital | $4.18 B |
| External capital saved | $3.60 B |
| Capital + lifetime external interest saved | $7.95 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $878.3 M | $131.7 M | $746.6 M |
| Stations | $413.7 M | $82.7 M | $331.0 M |
| Depots | $8.0 M | $2.0 M | $6.0 M |
| Rolling stock | $388.6 M | $136.0 M | $252.6 M |
| Dedicated solar plants | $387.3 M | $174.3 M | $213.0 M |
| Residual train control | $13.5 M | $6.7 M | $6.7 M |
| Charging microgrids | $23.8 M | $9.5 M | $14.3 M |
| EPC / project services | $126.6 M | $19.0 M | $107.6 M |
| Shared national trainset factory | $83.3 M | $16.7 M | $66.6 M |
| **Total** | **$2.32 B** | **$578.7 M** | **$1.74 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Lyon](Lyon/README.md) | 1,436,354 | 347 | $2.23 B | $561.2 M | $1.67 B |

## Local Basis And Regeneration

Country finance parameters use `FR` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 scripts/generate-national-briefs.py
```
