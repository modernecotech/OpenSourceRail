# Yemen National OpenSourceRail Strategy

This page contains only Yemen-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$13.71 B (88.3%) of external capital** and **$17.70 B of external interest**. Capital plus saved interest totals **$31.41 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 9 |
| Represented population | 8,337,500 |
| Trainsets / vehicle modules | 1,109 / 4,164 |
| City infrastructure and fleet CAPEX | $7.53 B |
| Shared national factory | $1.02 B |
| Factory sizing basis | 1,974 modules for Sanaa, then reused nationally |
| **Total national programme** | **$8.62 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.81 B (21.0%) |
| Domestic / local capital | $6.81 B (79.0%) |
| Annual external capital draw | $180.8 M / yr |
| Annual local capital draw | $681.1 M / yr |
| Annual public construction commitment | $1.20 B / yr for 10 years |
| Annual post-grace debt service | $1.10 B / yr |
| Default foreign-turnkey external capital | $15.51 B |
| External capital saved | $13.71 B |
| Capital + lifetime external interest saved | $31.41 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $4.12 B | $618.0 M | $3.50 B |
| Stations | $747.5 M | $149.5 M | $598.0 M |
| Depots | $552.9 M | $138.2 M | $414.7 M |
| Rolling stock | $1.20 B | $421.3 M | $782.4 M |
| Dedicated solar plants | $378.8 M | $170.4 M | $208.3 M |
| Residual train control | $23.7 M | $11.9 M | $11.9 M |
| Charging microgrids | $35.5 M | $14.2 M | $21.3 M |
| EPC / project services | $539.1 M | $80.9 M | $458.2 M |
| Shared national trainset factory | $1.02 B | $203.6 M | $814.5 M |
| **Total** | **$8.62 B** | **$1.81 B** | **$6.81 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Sanaa](Sanaa/README.md) | 3,937,500 | 329 | $3.38 B | $742.8 M | $2.63 B |
| [Aden](Aden/README.md) | 985,000 | 125 | $655.0 M | $136.3 M | $518.7 M |
| [Hodeidah](Hodeidah/README.md) | 750,000 | 78 | $428.7 M | $87.7 M | $341.0 M |
| [Ibb](Ibb/README.md) | 750,000 | 124 | $621.7 M | $129.9 M | $491.7 M |
| [Taiz](Taiz/README.md) | 615,000 | 125 | $600.2 M | $127.2 M | $473.1 M |
| [Mukalla](Mukalla/README.md) | 550,000 | 178 | $813.3 M | $174.9 M | $638.5 M |
| [Dhamar](Dhamar/README.md) | 300,000 | 48 | $320.0 M | $60.6 M | $259.4 M |
| [Lahij](Lahij/README.md) | 250,000 | 54 | $386.7 M | $72.6 M | $314.1 M |
| [Sayun](Sayun/README.md) | 200,000 | 48 | $327.2 M | $61.7 M | $265.4 M |

## Local Basis And Regeneration

Country finance parameters use `YE` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
