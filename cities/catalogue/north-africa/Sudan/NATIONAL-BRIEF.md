# Sudan National OpenSourceRail Strategy

This page contains only Sudan-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$21.45 B (88.4%) of external capital** and **$27.70 B of external interest**. Capital plus saved interest totals **$49.15 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 6 |
| Represented population | 10,729,000 |
| Trainsets / vehicle modules | 1,313 / 6,049 |
| City infrastructure and fleet CAPEX | $12.76 B |
| Shared national factory | $669.3 M |
| Factory sizing basis | 3,588 modules for Khartoum, then reused nationally |
| **Total national programme** | **$13.48 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $2.81 B (20.9%) |
| Domestic / local capital | $10.66 B (79.1%) |
| Annual external capital draw | $281.1 M / yr |
| Annual local capital draw | $1.07 B / yr |
| Annual public construction commitment | $1.62 B / yr for 10 years |
| Annual post-grace debt service | $1.47 B / yr |
| Default foreign-turnkey external capital | $24.26 B |
| External capital saved | $21.45 B |
| Capital + lifetime external interest saved | $49.15 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $7.03 B | $1.06 B | $5.98 B |
| Stations | $1.73 B | $346.9 M | $1.39 B |
| Depots | $588.0 M | $147.0 M | $441.0 M |
| Rolling stock | $1.72 B | $601.2 M | $1.12 B |
| Dedicated solar plants | $766.7 M | $345.0 M | $421.7 M |
| Residual train control | $37.3 M | $18.7 M | $18.7 M |
| Charging microgrids | $96.0 M | $38.4 M | $57.6 M |
| EPC / project services | $831.4 M | $124.7 M | $706.7 M |
| Shared national trainset factory | $669.3 M | $133.9 M | $535.5 M |
| **Total** | **$13.48 B** | **$2.81 B** | **$10.66 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Khartoum](Khartoum/README.md) | 5,829,000 | 598 | $6.90 B | $1.49 B | $5.41 B |
| [Omdurman](Omdurman/README.md) | 2,800,000 | 316 | $3.59 B | $720.3 M | $2.87 B |
| [Nyala](Nyala/README.md) | 600,000 | 126 | $737.8 M | $149.8 M | $587.9 M |
| [El Obeid](El-Obeid/README.md) | 500,000 | 122 | $618.6 M | $129.7 M | $488.9 M |
| [Kassala](Kassala/README.md) | 500,000 | 69 | $459.7 M | $90.6 M | $369.1 M |
| [Port Sudan](Port-Sudan/README.md) | 500,000 | 82 | $455.6 M | $92.8 M | $362.8 M |

## Local Basis And Regeneration

Country finance parameters use `SD` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
