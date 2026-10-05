# Sudan National OpenSourceRail Strategy

This page contains only Sudan-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$75.21 B (90.7%) of external capital** and **$97.15 B of external interest**. Capital plus saved interest totals **$172.36 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 7 |
| Represented population | 11,029,000 |
| Trainsets / vehicle modules | 1,353 / 6,129 |
| City infrastructure and fleet CAPEX | $45.35 B |
| Shared national factory | $669.3 M |
| Factory sizing basis | 3,588 modules for Khartoum, then reused nationally |
| **Total national programme** | **$46.07 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $7.71 B (16.7%) |
| Domestic / local capital | $38.36 B (83.3%) |
| Annual external capital draw | $771.1 M / yr |
| Annual local capital draw | $3.84 B / yr |
| Annual public construction commitment | $5.72 B / yr for 10 years |
| Annual post-grace debt service | $5.15 B / yr |
| Default foreign-turnkey external capital | $82.92 B |
| External capital saved | $75.21 B |
| Capital + lifetime external interest saved | $172.36 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $37.38 B | $5.61 B | $31.77 B |
| Stations | $1.78 B | $356.6 M | $1.43 B |
| Depots | $627.5 M | $156.9 M | $470.6 M |
| Rolling stock | $1.74 B | $609.0 M | $1.13 B |
| Dedicated solar plants | $766.7 M | $345.0 M | $421.7 M |
| Residual train control | $38.1 M | $19.0 M | $19.0 M |
| Charging microgrids | $97.2 M | $38.9 M | $58.3 M |
| EPC / project services | $2.96 B | $444.5 M | $2.52 B |
| Shared national trainset factory | $669.3 M | $133.9 M | $535.5 M |
| **Total** | **$46.07 B** | **$7.71 B** | **$38.36 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Khartoum](Khartoum/README.md) | 5,829,000 | 598 | $24.03 B | $4.06 B | $19.98 B |
| [Omdurman](Omdurman/README.md) | 2,800,000 | 316 | $18.73 B | $2.99 B | $15.74 B |
| [Nyala](Nyala/README.md) | 600,000 | 126 | $738.4 M | $149.9 M | $588.5 M |
| [El Obeid](El-Obeid/README.md) | 500,000 | 122 | $672.7 M | $137.8 M | $534.9 M |
| [Kassala](Kassala/README.md) | 500,000 | 69 | $459.7 M | $90.6 M | $369.1 M |
| [Port Sudan](Port-Sudan/README.md) | 500,000 | 82 | $455.6 M | $92.8 M | $362.8 M |
| [Waw](Waw/README.md) | 300,000 | 40 | $266.9 M | $51.4 M | $215.4 M |

## Local Basis And Regeneration

Country finance parameters use `SD` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
