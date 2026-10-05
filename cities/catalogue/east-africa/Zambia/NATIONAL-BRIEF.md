# Zambia National OpenSourceRail Strategy

This page contains only Zambia-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$8.18 B (87.8%) of external capital** and **$10.26 B of external interest**. Capital plus saved interest totals **$18.44 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 3,037,000 |
| Trainsets / vehicle modules | 384 / 2,304 |
| City infrastructure and fleet CAPEX | $4.23 B |
| Shared national factory | $889.3 M |
| Factory sizing basis | 2,304 modules for Lusaka, then reused nationally |
| **Total national programme** | **$5.18 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.14 B (21.9%) |
| Domestic / local capital | $4.04 B (78.1%) |
| Annual external capital draw | $162.3 M / yr |
| Annual local capital draw | $577.4 M / yr |
| Annual public construction commitment | $700.1 M / yr for 7 years |
| Annual post-grace debt service | $603.7 M / yr |
| Default foreign-turnkey external capital | $9.32 B |
| External capital saved | $8.18 B |
| Capital + lifetime external interest saved | $18.44 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $2.11 B | $316.1 M | $1.79 B |
| Stations | $564.3 M | $112.9 M | $451.4 M |
| Depots | $194.6 M | $48.6 M | $145.9 M |
| Rolling stock | $645.1 M | $225.8 M | $419.3 M |
| Dedicated solar plants | $416.3 M | $187.3 M | $229.0 M |
| Residual train control | $12.0 M | $6.0 M | $6.0 M |
| Charging microgrids | $37.4 M | $15.0 M | $22.4 M |
| EPC / project services | $311.5 M | $46.7 M | $264.8 M |
| Shared national trainset factory | $889.3 M | $177.9 M | $711.4 M |
| **Total** | **$5.18 B** | **$1.14 B** | **$4.04 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Lusaka](Lusaka/README.md) | 3,037,000 | 384 | $4.23 B | $949.1 M | $3.28 B |

## Local Basis And Regeneration

Country finance parameters use `ZM` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
