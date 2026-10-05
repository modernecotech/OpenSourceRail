# Cameroon National OpenSourceRail Strategy

This page contains only Cameroon-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$18.52 B (88.1%) of external capital** and **$23.22 B of external interest**. Capital plus saved interest totals **$41.74 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 10 |
| Represented population | 11,650,000 |
| Trainsets / vehicle modules | 1,369 / 5,755 |
| City infrastructure and fleet CAPEX | $10.67 B |
| Shared national factory | $942.1 M |
| Factory sizing basis | 1,668 modules for Douala, then reused nationally |
| **Total national programme** | **$11.68 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $2.51 B (21.5%) |
| Domestic / local capital | $9.17 B (78.5%) |
| Annual external capital draw | $358.2 M / yr |
| Annual local capital draw | $1.31 B / yr |
| Annual public construction commitment | $998.8 M / yr for 7 years |
| Annual post-grace debt service | $816.5 M / yr |
| Default foreign-turnkey external capital | $21.03 B |
| External capital saved | $18.52 B |
| Capital + lifetime external interest saved | $41.74 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $5.90 B | $885.5 M | $5.02 B |
| Stations | $940.1 M | $188.0 M | $752.1 M |
| Depots | $637.2 M | $159.3 M | $477.9 M |
| Rolling stock | $1.66 B | $580.7 M | $1.08 B |
| Dedicated solar plants | $803.3 M | $361.5 M | $441.8 M |
| Residual train control | $31.3 M | $15.6 M | $15.6 M |
| Charging microgrids | $53.2 M | $21.3 M | $31.9 M |
| EPC / project services | $711.7 M | $106.7 M | $604.9 M |
| Shared national trainset factory | $942.1 M | $188.4 M | $753.7 M |
| **Total** | **$11.68 B** | **$2.51 B** | **$9.17 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Yaounde](Yaounde/README.md) | 4,100,000 | 277 | $3.06 B | $685.1 M | $2.38 B |
| [Douala](Douala/README.md) | 3,900,000 | 278 | $3.17 B | $701.9 M | $2.46 B |
| [Bafoussam](Bafoussam/README.md) | 600,000 | 181 | $875.1 M | $189.0 M | $686.1 M |
| [Bamenda](Bamenda/README.md) | 600,000 | 132 | $671.4 M | $143.3 M | $528.2 M |
| [Garoua](Garoua/README.md) | 600,000 | 82 | $518.2 M | $102.2 M | $416.0 M |
| [Maroua](Maroua/README.md) | 500,000 | 142 | $811.8 M | $164.8 M | $647.0 M |
| [Kumba](Kumba/README.md) | 400,000 | 113 | $591.7 M | $125.0 M | $466.8 M |
| [Bertoua](Bertoua/README.md) | 350,000 | 77 | $434.9 M | $90.3 M | $344.6 M |
| [Ngaoundere](Ngaoundere/README.md) | 350,000 | 70 | $424.7 M | $85.2 M | $339.5 M |
| [Edea](Edea/README.md) | 250,000 | 17 | $117.3 M | $22.0 M | $95.2 M |

## Local Basis And Regeneration

Country finance parameters use `CM` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
