# Cameroon National OpenSourceRail Strategy

This page contains only Cameroon-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$11.32 B (85.8%) of external capital** and **$14.19 B of external interest**. Capital plus saved interest totals **$25.51 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 10 |
| Represented population | 11,650,000 |
| Trainsets / vehicle modules | 1,326 / 5,860 |
| City infrastructure and fleet CAPEX | $7.20 B |
| Shared national factory | $115.9 M |
| Factory sizing basis | 1,932 modules for Douala, then reused nationally |
| **Total national programme** | **$7.33 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.87 B (25.5%) |
| Domestic / local capital | $5.46 B (74.5%) |
| Annual external capital draw | $266.7 M / yr |
| Annual local capital draw | $779.8 M / yr |
| Annual public construction commitment | $611.2 M / yr for 7 years |
| Annual post-grace debt service | $507.8 M / yr |
| Default foreign-turnkey external capital | $13.19 B |
| External capital saved | $11.32 B |
| Capital + lifetime external interest saved | $25.51 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $2.51 B | $376.2 M | $2.13 B |
| Stations | $1.36 B | $271.5 M | $1.09 B |
| Depots | $80.0 M | $20.0 M | $60.0 M |
| Rolling stock | $1.68 B | $588.4 M | $1.09 B |
| Dedicated solar plants | $1.06 B | $479.1 M | $585.5 M |
| Residual train control | $37.5 M | $18.8 M | $18.8 M |
| Charging microgrids | $71.5 M | $28.6 M | $42.9 M |
| EPC / project services | $409.6 M | $61.4 M | $348.2 M |
| Shared national trainset factory | $115.9 M | $23.2 M | $92.7 M |
| **Total** | **$7.33 B** | **$1.87 B** | **$5.46 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Yaounde](Yaounde/README.md) | 4,100,000 | 312 | $2.13 B | $574.6 M | $1.56 B |
| [Douala](Douala/README.md) | 3,900,000 | 322 | $2.38 B | $618.3 M | $1.76 B |
| [Bafoussam](Bafoussam/README.md) | 600,000 | 158 | $546.6 M | $139.9 M | $406.7 M |
| [Bamenda](Bamenda/README.md) | 600,000 | 111 | $405.3 M | $102.3 M | $302.9 M |
| [Garoua](Garoua/README.md) | 600,000 | 73 | $318.8 M | $71.8 M | $247.0 M |
| [Maroua](Maroua/README.md) | 500,000 | 113 | $453.4 M | $105.8 M | $347.5 M |
| [Kumba](Kumba/README.md) | 400,000 | 90 | $336.5 M | $84.4 M | $252.0 M |
| [Bertoua](Bertoua/README.md) | 350,000 | 63 | $270.2 M | $65.0 M | $205.3 M |
| [Ngaoundere](Ngaoundere/README.md) | 350,000 | 64 | $282.2 M | $64.6 M | $217.6 M |
| [Edea](Edea/README.md) | 250,000 | 20 | $73.1 M | $15.9 M | $57.2 M |

## Local Basis And Regeneration

Country finance parameters use `CM` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 scripts/generate-national-briefs.py
```
