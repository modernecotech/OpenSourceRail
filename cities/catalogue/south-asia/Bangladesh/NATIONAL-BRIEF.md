# Bangladesh National OpenSourceRail Strategy

This page contains only Bangladesh-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$27.83 B (88.3%) of external capital** and **$34.89 B of external interest**. Capital plus saved interest totals **$62.72 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 10 |
| Represented population | 13,550,000 |
| Trainsets / vehicle modules | 1,955 / 7,744 |
| City infrastructure and fleet CAPEX | $16.76 B |
| Shared national factory | $698.7 M |
| Factory sizing basis | 2,670 modules for Chittagong, then reused nationally |
| **Total national programme** | **$17.51 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $3.68 B (21.0%) |
| Domestic / local capital | $13.83 B (79.0%) |
| Annual external capital draw | $525.4 M / yr |
| Annual local capital draw | $1.98 B / yr |
| Annual public construction commitment | $1.50 B / yr for 7 years |
| Annual post-grace debt service | $1.22 B / yr |
| Default foreign-turnkey external capital | $31.51 B |
| External capital saved | $27.83 B |
| Capital + lifetime external interest saved | $62.72 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $9.74 B | $1.46 B | $8.28 B |
| Stations | $1.56 B | $312.1 M | $1.25 B |
| Depots | $840.3 M | $210.1 M | $630.2 M |
| Rolling stock | $2.23 B | $779.2 M | $1.45 B |
| Dedicated solar plants | $1.24 B | $555.9 M | $679.5 M |
| Residual train control | $50.7 M | $25.4 M | $25.4 M |
| Charging microgrids | $84.9 M | $34.0 M | $50.9 M |
| EPC / project services | $1.06 B | $159.7 M | $904.8 M |
| Shared national trainset factory | $698.7 M | $139.7 M | $559.0 M |
| **Total** | **$17.51 B** | **$3.68 B** | **$13.83 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Chittagong](Chittagong/README.md) | 5,200,000 | 445 | $5.05 B | $1.12 B | $3.93 B |
| [Khulna](Khulna/README.md) | 1,500,000 | 223 | $2.93 B | $577.6 M | $2.35 B |
| [Gazipur](Gazipur/README.md) | 1,400,000 | 321 | $3.40 B | $709.4 M | $2.69 B |
| [Narayanganj](Narayanganj/README.md) | 950,000 | 205 | $1.07 B | $227.8 M | $846.7 M |
| [Rajshahi](Rajshahi/README.md) | 950,000 | 101 | $536.0 M | $113.0 M | $423.1 M |
| [Sylhet](Sylhet/README.md) | 900,000 | 126 | $662.9 M | $139.9 M | $523.0 M |
| [Rangpur](Rangpur/README.md) | 800,000 | 119 | $661.2 M | $138.4 M | $522.8 M |
| [Mymensingh](Mymensingh/README.md) | 700,000 | 115 | $705.1 M | $143.7 M | $561.4 M |
| [Comilla](Comilla/README.md) | 600,000 | 137 | $762.7 M | $159.2 M | $603.5 M |
| [Barisal](Barisal/README.md) | 550,000 | 163 | $968.3 M | $199.3 M | $769.0 M |

## Local Basis And Regeneration

Country finance parameters use `BD` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
