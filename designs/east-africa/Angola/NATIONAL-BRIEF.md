# Angola National OpenSourceRail Strategy

This page contains only Angola-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$10.32 B (85.8%) of external capital** and **$12.69 B of external interest**. Capital plus saved interest totals **$23.01 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 9 |
| Represented population | 13,135,000 |
| Trainsets / vehicle modules | 1,254 / 5,481 |
| City infrastructure and fleet CAPEX | $6.45 B |
| Shared national factory | $223.9 M |
| Factory sizing basis | 3,732 modules for Luanda, then reused nationally |
| **Total national programme** | **$6.69 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.71 B (25.6%) |
| Domestic / local capital | $4.97 B (74.4%) |
| Annual external capital draw | $342.8 M / yr |
| Annual local capital draw | $994.5 M / yr |
| Annual public construction commitment | $733.5 M / yr for 5 years |
| Annual post-grace debt service | $566.0 M / yr |
| Default foreign-turnkey external capital | $12.04 B |
| External capital saved | $10.32 B |
| Capital + lifetime external interest saved | $23.01 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $2.07 B | $310.8 M | $1.76 B |
| Stations | $1.33 B | $266.0 M | $1.06 B |
| Depots | $72.0 M | $18.0 M | $54.0 M |
| Rolling stock | $1.56 B | $547.3 M | $1.02 B |
| Dedicated solar plants | $952.7 M | $428.7 M | $524.0 M |
| Residual train control | $34.1 M | $17.1 M | $17.1 M |
| Charging microgrids | $63.0 M | $25.2 M | $37.8 M |
| EPC / project services | $375.1 M | $56.3 M | $318.8 M |
| Shared national trainset factory | $223.9 M | $44.8 M | $179.1 M |
| **Total** | **$6.69 B** | **$1.71 B** | **$4.97 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Luanda](Luanda/README.md) | 9,085,000 | 622 | $4.06 B | $1.11 B | $2.95 B |
| [Huambo](Huambo/README.md) | 800,000 | 112 | $409.3 M | $98.6 M | $310.8 M |
| [Lubango](Lubango/README.md) | 700,000 | 119 | $442.1 M | $105.9 M | $336.2 M |
| [Benguela](Benguela/README.md) | 600,000 | 110 | $393.2 M | $95.0 M | $298.2 M |
| [Lobito](Lobito/README.md) | 500,000 | 83 | $299.3 M | $72.4 M | $226.9 M |
| [Malanje](Malanje/README.md) | 500,000 | 34 | $163.1 M | $37.6 M | $125.5 M |
| [Uige](Uige/README.md) | 400,000 | 27 | $98.0 M | $24.1 M | $73.9 M |
| [Namibe](Namibe/README.md) | 300,000 | 84 | $285.0 M | $62.5 M | $222.5 M |
| [Soyo](Soyo/README.md) | 250,000 | 63 | $295.4 M | $62.7 M | $232.7 M |

## Local Basis And Regeneration

Country finance parameters use `AO` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 scripts/generate-national-briefs.py
```
