# Afghanistan National OpenSourceRail Strategy

This page contains only Afghanistan-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$11.43 B (88.3%) of external capital** and **$14.76 B of external interest**. Capital plus saved interest totals **$26.18 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 5 |
| Represented population | 7,051,000 |
| Trainsets / vehicle modules | 846 / 3,426 |
| City infrastructure and fleet CAPEX | $6.13 B |
| Shared national factory | $990.6 M |
| Factory sizing basis | 1,776 modules for Kabul, then reused nationally |
| **Total national programme** | **$7.19 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.51 B (21.0%) |
| Domestic / local capital | $5.68 B (79.0%) |
| Annual external capital draw | $151.1 M / yr |
| Annual local capital draw | $567.6 M / yr |
| Annual public construction commitment | $998.8 M / yr for 10 years |
| Annual post-grace debt service | $915.8 M / yr |
| Default foreign-turnkey external capital | $12.94 B |
| External capital saved | $11.43 B |
| Capital + lifetime external interest saved | $26.18 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $3.39 B | $508.2 M | $2.88 B |
| Stations | $594.7 M | $118.9 M | $475.8 M |
| Depots | $378.7 M | $94.7 M | $284.0 M |
| Rolling stock | $992.3 M | $347.3 M | $645.0 M |
| Dedicated solar plants | $342.9 M | $154.3 M | $188.6 M |
| Residual train control | $18.6 M | $9.3 M | $9.3 M |
| Charging microgrids | $33.6 M | $13.4 M | $20.2 M |
| EPC / project services | $447.8 M | $67.2 M | $380.6 M |
| Shared national trainset factory | $990.6 M | $198.1 M | $792.5 M |
| **Total** | **$7.19 B** | **$1.51 B** | **$5.68 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Kabul](Kabul/README.md) | 4,601,000 | 296 | $3.28 B | $710.0 M | $2.57 B |
| [Herat](Herat/README.md) | 800,000 | 125 | $636.6 M | $133.0 M | $503.6 M |
| [Kandahar](Kandahar/README.md) | 700,000 | 129 | $681.5 M | $141.2 M | $540.3 M |
| [Mazar E Sharif](Mazar-E-Sharif/README.md) | 600,000 | 170 | $852.5 M | $178.9 M | $673.6 M |
| [Jalalabad Af](Jalalabad-Af/README.md) | 350,000 | 126 | $677.5 M | $139.8 M | $537.6 M |

## Local Basis And Regeneration

Country finance parameters use `AF` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
