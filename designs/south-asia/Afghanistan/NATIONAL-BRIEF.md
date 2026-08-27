# Afghanistan National OpenSourceRail Strategy

This page contains only Afghanistan-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$6.51 B (86.1%) of external capital** and **$8.41 B of external interest**. Capital plus saved interest totals **$14.92 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 5 |
| Represented population | 7,051,000 |
| Trainsets / vehicle modules | 822 / 3,516 |
| City infrastructure and fleet CAPEX | $4.06 B |
| Shared national factory | $126.0 M |
| Factory sizing basis | 2,100 modules for Kabul, then reused nationally |
| **Total national programme** | **$4.20 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.05 B (24.9%) |
| Domestic / local capital | $3.15 B (75.1%) |
| Annual external capital draw | $104.7 M / yr |
| Annual local capital draw | $315.1 M / yr |
| Annual public construction commitment | $563.8 M / yr for 10 years |
| Annual post-grace debt service | $521.1 M / yr |
| Default foreign-turnkey external capital | $7.55 B |
| External capital saved | $6.51 B |
| Capital + lifetime external interest saved | $14.92 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $1.41 B | $212.0 M | $1.20 B |
| Stations | $813.7 M | $162.7 M | $651.0 M |
| Depots | $40.0 M | $10.0 M | $30.0 M |
| Rolling stock | $1.01 B | $354.5 M | $658.3 M |
| Dedicated solar plants | $483.8 M | $217.7 M | $266.1 M |
| Residual train control | $22.1 M | $11.1 M | $11.1 M |
| Charging microgrids | $42.2 M | $16.9 M | $25.3 M |
| EPC / project services | $242.9 M | $36.4 M | $206.5 M |
| Shared national trainset factory | $126.0 M | $25.2 M | $100.8 M |
| **Total** | **$4.20 B** | **$1.05 B** | **$3.15 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Kabul](Kabul/README.md) | 4,601,000 | 350 | $2.33 B | $601.3 M | $1.73 B |
| [Herat](Herat/README.md) | 800,000 | 108 | $431.8 M | $102.0 M | $329.7 M |
| [Kandahar](Kandahar/README.md) | 700,000 | 113 | $440.4 M | $105.9 M | $334.5 M |
| [Mazar E Sharif](Mazar-E-Sharif/README.md) | 600,000 | 139 | $489.0 M | $119.7 M | $369.3 M |
| [Jalalabad Af](Jalalabad-Af/README.md) | 350,000 | 112 | $368.7 M | $91.2 M | $277.6 M |

## Local Basis And Regeneration

Country finance parameters use `AF` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 scripts/generate-national-briefs.py
```
