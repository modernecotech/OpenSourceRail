# Afghanistan National OpenSourceRail Strategy

This page contains only Afghanistan-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$12.03 B (88.3%) of external capital** and **$15.54 B of external interest**. Capital plus saved interest totals **$27.57 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 5 |
| Represented population | 7,051,000 |
| Trainsets / vehicle modules | 881 / 3,603 |
| City infrastructure and fleet CAPEX | $6.48 B |
| Shared national factory | $1.02 B |
| Factory sizing basis | 1,920 modules for Kabul, then reused nationally |
| **Total national programme** | **$7.57 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.59 B (21.1%) |
| Domestic / local capital | $5.98 B (78.9%) |
| Annual external capital draw | $159.5 M / yr |
| Annual local capital draw | $597.6 M / yr |
| Annual public construction commitment | $1.05 B / yr for 10 years |
| Annual post-grace debt service | $964.4 M / yr |
| Default foreign-turnkey external capital | $13.63 B |
| External capital saved | $12.03 B |
| Capital + lifetime external interest saved | $27.57 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $3.41 B | $511.3 M | $2.90 B |
| Stations | $841.5 M | $168.3 M | $673.2 M |
| Depots | $386.3 M | $96.6 M | $289.7 M |
| Rolling stock | $1.04 B | $364.9 M | $677.6 M |
| Dedicated solar plants | $340.2 M | $153.1 M | $187.1 M |
| Residual train control | $18.8 M | $9.4 M | $9.4 M |
| Charging microgrids | $41.0 M | $16.4 M | $24.6 M |
| EPC / project services | $473.0 M | $70.9 M | $402.0 M |
| Shared national trainset factory | $1.02 B | $203.6 M | $814.5 M |
| **Total** | **$7.57 B** | **$1.59 B** | **$5.98 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Kabul](Kabul/README.md) | 4,601,000 | 320 | $3.50 B | $759.6 M | $2.74 B |
| [Herat](Herat/README.md) | 800,000 | 124 | $659.1 M | $137.0 M | $522.0 M |
| [Kandahar](Kandahar/README.md) | 700,000 | 130 | $707.2 M | $146.4 M | $560.9 M |
| [Mazar E Sharif](Mazar-E-Sharif/README.md) | 600,000 | 177 | $900.2 M | $189.6 M | $710.7 M |
| [Jalalabad Af](Jalalabad-Af/README.md) | 350,000 | 130 | $716.8 M | $147.6 M | $569.2 M |

## Local Basis And Regeneration

Country finance parameters use `AF` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
