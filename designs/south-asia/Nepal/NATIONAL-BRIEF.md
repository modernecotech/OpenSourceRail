# Nepal National OpenSourceRail Strategy

This page contains only Nepal-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$4.69 B (87.1%) of external capital** and **$5.88 B of external interest**. Capital plus saved interest totals **$10.57 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 3 |
| Represented population | 2,342,000 |
| Trainsets / vehicle modules | 483 / 1,626 |
| City infrastructure and fleet CAPEX | $2.93 B |
| Shared national factory | $58.6 M |
| Factory sizing basis | 976 modules for Kathmandu, then reused nationally |
| **Total national programme** | **$2.99 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $695.9 M (23.3%) |
| Domestic / local capital | $2.30 B (76.7%) |
| Annual external capital draw | $99.4 M / yr |
| Annual local capital draw | $328.1 M / yr |
| Annual public construction commitment | $234.7 M / yr for 7 years |
| Annual post-grace debt service | $192.6 M / yr |
| Default foreign-turnkey external capital | $5.39 B |
| External capital saved | $4.69 B |
| Capital + lifetime external interest saved | $10.57 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $1.26 B | $189.7 M | $1.07 B |
| Stations | $612.2 M | $122.4 M | $489.8 M |
| Depots | $24.0 M | $6.0 M | $18.0 M |
| Rolling stock | $465.6 M | $163.0 M | $302.6 M |
| Dedicated solar plants | $354.5 M | $159.5 M | $195.0 M |
| Residual train control | $15.5 M | $7.8 M | $7.8 M |
| Charging microgrids | $25.0 M | $10.0 M | $15.0 M |
| EPC / project services | $172.6 M | $25.9 M | $146.7 M |
| Shared national trainset factory | $58.6 M | $11.7 M | $46.8 M |
| **Total** | **$2.99 B** | **$695.9 M** | **$2.30 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Kathmandu](Kathmandu/README.md) | 1,442,000 | 244 | $1.86 B | $446.8 M | $1.41 B |
| [Pokhara](Pokhara/README.md) | 600,000 | 172 | $638.1 M | $154.4 M | $483.7 M |
| [Biratnagar](Biratnagar/README.md) | 300,000 | 67 | $433.1 M | $82.4 M | $350.7 M |

## Local Basis And Regeneration

Country finance parameters use `NP` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 scripts/generate-national-briefs.py
```
