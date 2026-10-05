# Nigeria National OpenSourceRail Strategy

This page contains only Nigeria-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$34.46 B (88.6%) of external capital** and **$43.20 B of external interest**. Capital plus saved interest totals **$77.66 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 10 |
| Represented population | 19,200,000 |
| Trainsets / vehicle modules | 1,930 / 8,920 |
| City infrastructure and fleet CAPEX | $20.91 B |
| Shared national factory | $647.9 M |
| Factory sizing basis | 3,810 modules for Kano, then reused nationally |
| **Total national programme** | **$21.60 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $4.42 B (20.5%) |
| Domestic / local capital | $17.18 B (79.5%) |
| Annual external capital draw | $632.1 M / yr |
| Annual local capital draw | $2.45 B / yr |
| Annual public construction commitment | $2.55 B / yr for 7 years |
| Annual post-grace debt service | $2.14 B / yr |
| Default foreign-turnkey external capital | $38.89 B |
| External capital saved | $34.46 B |
| Capital + lifetime external interest saved | $77.66 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $12.81 B | $1.92 B | $10.89 B |
| Stations | $1.80 B | $359.7 M | $1.44 B |
| Depots | $944.6 M | $236.2 M | $708.5 M |
| Rolling stock | $2.52 B | $882.6 M | $1.64 B |
| Dedicated solar plants | $1.37 B | $616.8 M | $753.9 M |
| Residual train control | $62.0 M | $31.0 M | $31.0 M |
| Charging microgrids | $120.4 M | $48.2 M | $72.2 M |
| EPC / project services | $1.32 B | $198.5 M | $1.13 B |
| Shared national trainset factory | $647.9 M | $129.6 M | $518.3 M |
| **Total** | **$21.60 B** | **$4.42 B** | **$17.18 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Kano](Kano/README.md) | 4,200,000 | 635 | $6.82 B | $1.47 B | $5.35 B |
| [Ibadan](Ibadan/README.md) | 3,900,000 | 167 | $1.90 B | $421.8 M | $1.47 B |
| [Port Harcourt](Port-Harcourt/README.md) | 3,000,000 | 204 | $2.58 B | $516.8 M | $2.06 B |
| [Benin City](Benin-City/README.md) | 1,800,000 | 152 | $1.63 B | $333.4 M | $1.29 B |
| [Onitsha](Onitsha/README.md) | 1,500,000 | 185 | $2.24 B | $453.5 M | $1.78 B |
| [Maiduguri](Maiduguri/README.md) | 1,200,000 | 183 | $3.49 B | $623.8 M | $2.86 B |
| [Ilorin](Ilorin/README.md) | 1,000,000 | 124 | $681.1 M | $143.2 M | $538.0 M |
| [Aba Ng](Aba-Ng/README.md) | 900,000 | 80 | $473.3 M | $97.8 M | $375.6 M |
| [Jos](Jos/README.md) | 900,000 | 116 | $642.7 M | $130.3 M | $512.4 M |
| [Uyo](Uyo/README.md) | 800,000 | 84 | $466.5 M | $97.4 M | $369.2 M |

## Local Basis And Regeneration

Country finance parameters use `NG` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
