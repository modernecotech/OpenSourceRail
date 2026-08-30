# Nigeria National OpenSourceRail Strategy

This page contains only Nigeria-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$21.20 B (86.4%) of external capital** and **$26.58 B of external interest**. Capital plus saved interest totals **$47.78 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 10 |
| Represented population | 19,200,000 |
| Trainsets / vehicle modules | 2,078 / 9,756 |
| City infrastructure and fleet CAPEX | $13.37 B |
| Shared national factory | $247.0 M |
| Factory sizing basis | 4,116 modules for Kano, then reused nationally |
| **Total national programme** | **$13.63 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $3.34 B (24.5%) |
| Domestic / local capital | $10.29 B (75.5%) |
| Annual external capital draw | $476.9 M / yr |
| Annual local capital draw | $1.47 B / yr |
| Annual public construction commitment | $1.56 B / yr for 7 years |
| Annual post-grace debt service | $1.33 B / yr |
| Default foreign-turnkey external capital | $24.54 B |
| External capital saved | $21.20 B |
| Capital + lifetime external interest saved | $47.78 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $5.10 B | $765.0 M | $4.33 B |
| Stations | $2.70 B | $540.8 M | $2.16 B |
| Depots | $80.0 M | $20.0 M | $60.0 M |
| Rolling stock | $2.75 B | $963.9 M | $1.79 B |
| Dedicated solar plants | $1.74 B | $785.2 M | $959.7 M |
| Residual train control | $70.6 M | $35.3 M | $35.3 M |
| Charging microgrids | $155.0 M | $62.0 M | $93.0 M |
| EPC / project services | $777.7 M | $116.7 M | $661.1 M |
| Shared national trainset factory | $247.0 M | $49.4 M | $197.6 M |
| **Total** | **$13.63 B** | **$3.34 B** | **$10.29 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Kano](Kano/README.md) | 4,200,000 | 686 | $4.41 B | $1.14 B | $3.28 B |
| [Ibadan](Ibadan/README.md) | 3,900,000 | 222 | $1.58 B | $414.0 M | $1.17 B |
| [Port Harcourt](Port-Harcourt/README.md) | 3,000,000 | 232 | $1.70 B | $404.3 M | $1.30 B |
| [Benin City](Benin-City/README.md) | 1,800,000 | 171 | $1.18 B | $282.1 M | $900.9 M |
| [Onitsha](Onitsha/README.md) | 1,500,000 | 198 | $1.50 B | $355.1 M | $1.14 B |
| [Maiduguri](Maiduguri/README.md) | 1,200,000 | 197 | $1.50 B | $333.4 M | $1.16 B |
| [Ilorin](Ilorin/README.md) | 1,000,000 | 124 | $502.5 M | $122.0 M | $380.5 M |
| [Aba Ng](Aba-Ng/README.md) | 900,000 | 70 | $282.8 M | $68.7 M | $214.0 M |
| [Jos](Jos/README.md) | 900,000 | 102 | $390.1 M | $92.0 M | $298.1 M |
| [Uyo](Uyo/README.md) | 800,000 | 76 | $315.8 M | $76.0 M | $239.8 M |

## Local Basis And Regeneration

Country finance parameters use `NG` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
