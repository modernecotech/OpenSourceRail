# Yemen National OpenSourceRail Strategy

This page contains only Yemen-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$15.13 B (88.4%) of external capital** and **$19.55 B of external interest**. Capital plus saved interest totals **$34.68 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 9 |
| Represented population | 8,337,500 |
| Trainsets / vehicle modules | 1,192 / 4,466 |
| City infrastructure and fleet CAPEX | $8.42 B |
| Shared national factory | $1.02 B |
| Factory sizing basis | 2,082 modules for Sanaa, then reused nationally |
| **Total national programme** | **$9.51 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.99 B (20.9%) |
| Domestic / local capital | $7.52 B (79.1%) |
| Annual external capital draw | $199.2 M / yr |
| Annual local capital draw | $752.2 M / yr |
| Annual public construction commitment | $1.32 B / yr for 10 years |
| Annual post-grace debt service | $1.21 B / yr |
| Default foreign-turnkey external capital | $17.13 B |
| External capital saved | $15.13 B |
| Capital + lifetime external interest saved | $34.68 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $4.28 B | $641.4 M | $3.63 B |
| Stations | $1.31 B | $262.7 M | $1.05 B |
| Depots | $567.6 M | $141.9 M | $425.7 M |
| Rolling stock | $1.29 B | $452.2 M | $839.9 M |
| Dedicated solar plants | $377.0 M | $169.7 M | $207.4 M |
| Residual train control | $24.4 M | $12.2 M | $12.2 M |
| Charging microgrids | $47.7 M | $19.1 M | $28.6 M |
| EPC / project services | $597.8 M | $89.7 M | $508.1 M |
| Shared national trainset factory | $1.02 B | $203.6 M | $814.5 M |
| **Total** | **$9.51 B** | **$1.99 B** | **$7.52 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Sanaa](Sanaa/README.md) | 3,937,500 | 347 | $3.61 B | $793.8 M | $2.81 B |
| [Aden](Aden/README.md) | 985,000 | 156 | $885.1 M | $182.4 M | $702.7 M |
| [Hodeidah](Hodeidah/README.md) | 750,000 | 79 | $454.6 M | $92.8 M | $361.7 M |
| [Ibb](Ibb/README.md) | 750,000 | 127 | $639.4 M | $133.8 M | $505.6 M |
| [Taiz](Taiz/README.md) | 615,000 | 121 | $605.1 M | $127.5 M | $477.6 M |
| [Mukalla](Mukalla/README.md) | 550,000 | 211 | $1.17 B | $246.6 M | $921.6 M |
| [Dhamar](Dhamar/README.md) | 300,000 | 48 | $324.7 M | $61.5 M | $263.2 M |
| [Lahij](Lahij/README.md) | 250,000 | 54 | $401.2 M | $75.5 M | $325.8 M |
| [Sayun](Sayun/README.md) | 200,000 | 49 | $339.5 M | $64.2 M | $275.3 M |

## Local Basis And Regeneration

Country finance parameters use `YE` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
