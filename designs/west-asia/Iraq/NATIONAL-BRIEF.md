# Iraq National OpenSourceRail Strategy

This page contains only Iraq-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$32.28 B (86.4%) of external capital** and **$39.68 B of external interest**. Capital plus saved interest totals **$71.96 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 18 |
| Represented population | 29,491,199 |
| Trainsets / vehicle modules | 3,603 / 15,714 |
| City infrastructure and fleet CAPEX | $20.46 B |
| Shared national factory | $282.2 M |
| Factory sizing basis | 4,704 modules for Baghdad, then reused nationally |
| **Total national programme** | **$20.76 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $5.10 B (24.5%) |
| Domestic / local capital | $15.67 B (75.5%) |
| Annual external capital draw | $1.02 B / yr |
| Annual local capital draw | $3.13 B / yr |
| Annual public construction commitment | $1.92 B / yr for 5 years |
| Annual post-grace debt service | $1.42 B / yr |
| Default foreign-turnkey external capital | $37.37 B |
| External capital saved | $32.28 B |
| Capital + lifetime external interest saved | $71.96 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $7.99 B | $1.20 B | $6.79 B |
| Stations | $3.77 B | $754.8 M | $3.02 B |
| Depots | $144.0 M | $36.0 M | $108.0 M |
| Rolling stock | $4.47 B | $1.56 B | $2.91 B |
| Dedicated solar plants | $2.59 B | $1.17 B | $1.43 B |
| Residual train control | $113.7 M | $56.8 M | $56.8 M |
| Charging microgrids | $206.3 M | $82.5 M | $123.8 M |
| EPC / project services | $1.19 B | $178.3 M | $1.01 B |
| Shared national trainset factory | $282.2 M | $56.4 M | $225.8 M |
| **Total** | **$20.76 B** | **$5.10 B** | **$15.67 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Baghdad](Baghdad/README.md) | 9,780,429 | 784 | $4.72 B | $1.27 B | $3.45 B |
| [Basra](Basra/README.md) | 3,955,000 | 450 | $3.11 B | $793.5 M | $2.32 B |
| [Sulaymaniyah](Sulaymaniyah/README.md) | 2,150,000 | 129 | $1.03 B | $243.5 M | $783.0 M |
| [Erbil](Erbil/README.md) | 1,952,000 | 212 | $1.02 B | $262.0 M | $758.5 M |
| [Mosul](Mosul/README.md) | 1,940,000 | 256 | $1.93 B | $431.6 M | $1.50 B |
| [Kirkuk](Kirkuk/README.md) | 1,780,000 | 179 | $1.17 B | $273.5 M | $893.6 M |
| [Najaf](Najaf/README.md) | 1,540,000 | 229 | $1.52 B | $354.4 M | $1.17 B |
| [Karbala](Karbala/README.md) | 1,390,000 | 198 | $1.37 B | $319.5 M | $1.05 B |
| [Nasiriyah](Nasiriyah/README.md) | 705,000 | 147 | $538.7 M | $125.7 M | $413.0 M |
| [Hillah](Hillah/README.md) | 700,000 | 125 | $461.2 M | $111.8 M | $349.4 M |
| [Amarah](Amarah/README.md) | 660,000 | 101 | $433.0 M | $99.4 M | $333.6 M |
| [Ramadi](Ramadi/README.md) | 525,000 | 104 | $430.3 M | $101.4 M | $328.9 M |
| [Baqubah](Baqubah/README.md) | 470,000 | 130 | $479.2 M | $116.4 M | $362.8 M |
| [Diwaniyah](Diwaniyah/README.md) | 440,000 | 106 | $434.5 M | $101.5 M | $333.1 M |
| [Kut](Kut/README.md) | 410,000 | 101 | $426.6 M | $97.9 M | $328.7 M |
| [Samawah](Samawah/README.md) | 373,770 | 108 | $415.3 M | $100.0 M | $315.4 M |
| [Duhok](Duhok/README.md) | 360,000 | 122 | $518.5 M | $127.7 M | $390.8 M |
| [Fallujah](Fallujah/README.md) | 360,000 | 122 | $452.4 M | $109.5 M | $342.9 M |

## Local Basis And Regeneration

Country finance parameters use `IQ` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 scripts/generate-national-briefs.py
```
