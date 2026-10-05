# Yemen National OpenSourceRail Strategy

This page contains only Yemen-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$30.58 B (90.0%) of external capital** and **$39.50 B of external interest**. Capital plus saved interest totals **$70.08 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 9 |
| Represented population | 8,337,500 |
| Trainsets / vehicle modules | 1,192 / 4,466 |
| City infrastructure and fleet CAPEX | $17.78 B |
| Shared national factory | $1.02 B |
| Factory sizing basis | 2,082 modules for Sanaa, then reused nationally |
| **Total national programme** | **$18.87 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $3.40 B (18.0%) |
| Domestic / local capital | $15.48 B (82.0%) |
| Annual external capital draw | $339.6 M / yr |
| Annual local capital draw | $1.55 B / yr |
| Annual public construction commitment | $2.69 B / yr for 10 years |
| Annual post-grace debt service | $2.45 B / yr |
| Default foreign-turnkey external capital | $33.97 B |
| External capital saved | $30.58 B |
| Capital + lifetime external interest saved | $70.08 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $13.02 B | $1.95 B | $11.07 B |
| Stations | $1.31 B | $262.7 M | $1.05 B |
| Depots | $567.6 M | $141.9 M | $425.7 M |
| Rolling stock | $1.29 B | $452.2 M | $839.9 M |
| Dedicated solar plants | $377.0 M | $169.7 M | $207.4 M |
| Residual train control | $24.4 M | $12.2 M | $12.2 M |
| Charging microgrids | $47.7 M | $19.1 M | $28.6 M |
| EPC / project services | $1.21 B | $181.5 M | $1.03 B |
| Shared national trainset factory | $1.02 B | $203.6 M | $814.5 M |
| **Total** | **$18.87 B** | **$3.40 B** | **$15.48 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Sanaa](Sanaa/README.md) | 3,937,500 | 347 | $4.07 B | $863.5 M | $3.21 B |
| [Aden](Aden/README.md) | 985,000 | 156 | $4.74 B | $761.2 M | $3.98 B |
| [Hodeidah](Hodeidah/README.md) | 750,000 | 79 | $2.16 B | $348.7 M | $1.81 B |
| [Ibb](Ibb/README.md) | 750,000 | 127 | $639.4 M | $133.8 M | $505.6 M |
| [Taiz](Taiz/README.md) | 615,000 | 121 | $605.1 M | $127.5 M | $477.6 M |
| [Mukalla](Mukalla/README.md) | 550,000 | 211 | $4.50 B | $746.3 M | $3.75 B |
| [Dhamar](Dhamar/README.md) | 300,000 | 48 | $324.7 M | $61.5 M | $263.2 M |
| [Lahij](Lahij/README.md) | 250,000 | 54 | $401.2 M | $75.5 M | $325.8 M |
| [Sayun](Sayun/README.md) | 200,000 | 49 | $339.5 M | $64.2 M | $275.3 M |

## Local Basis And Regeneration

Country finance parameters use `YE` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
