# Bangladesh National OpenSourceRail Strategy

This page contains only Bangladesh-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$17.27 B (86.2%) of external capital** and **$21.65 B of external interest**. Capital plus saved interest totals **$38.93 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 10 |
| Represented population | 13,550,000 |
| Trainsets / vehicle modules | 1,901 / 7,844 |
| City infrastructure and fleet CAPEX | $10.93 B |
| Shared national factory | $186.1 M |
| Factory sizing basis | 3,102 modules for Chittagong, then reused nationally |
| **Total national programme** | **$11.13 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $2.76 B (24.8%) |
| Domestic / local capital | $8.37 B (75.2%) |
| Annual external capital draw | $393.7 M / yr |
| Annual local capital draw | $1.20 B / yr |
| Annual public construction commitment | $932.5 M / yr for 7 years |
| Annual post-grace debt service | $772.5 M / yr |
| Default foreign-turnkey external capital | $20.03 B |
| External capital saved | $17.27 B |
| Capital + lifetime external interest saved | $38.93 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $4.17 B | $624.8 M | $3.54 B |
| Stations | $2.10 B | $419.9 M | $1.68 B |
| Depots | $80.0 M | $20.0 M | $60.0 M |
| Rolling stock | $2.24 B | $785.4 M | $1.46 B |
| Dedicated solar plants | $1.57 B | $705.5 M | $862.3 M |
| Residual train control | $57.9 M | $28.9 M | $28.9 M |
| Charging microgrids | $101.1 M | $40.4 M | $60.7 M |
| EPC / project services | $625.4 M | $93.8 M | $531.6 M |
| Shared national trainset factory | $186.1 M | $37.2 M | $148.9 M |
| **Total** | **$11.13 B** | **$2.76 B** | **$8.37 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Chittagong](Chittagong/README.md) | 5,200,000 | 517 | $3.50 B | $933.4 M | $2.56 B |
| [Khulna](Khulna/README.md) | 1,500,000 | 252 | $1.81 B | $428.1 M | $1.38 B |
| [Gazipur](Gazipur/README.md) | 1,400,000 | 338 | $2.32 B | $560.3 M | $1.76 B |
| [Narayanganj](Narayanganj/README.md) | 950,000 | 157 | $657.8 M | $158.1 M | $499.7 M |
| [Rajshahi](Rajshahi/README.md) | 950,000 | 93 | $410.8 M | $97.6 M | $313.2 M |
| [Sylhet](Sylhet/README.md) | 900,000 | 109 | $408.8 M | $101.4 M | $307.4 M |
| [Rangpur](Rangpur/README.md) | 800,000 | 99 | $388.7 M | $95.8 M | $293.0 M |
| [Mymensingh](Mymensingh/README.md) | 700,000 | 92 | $459.0 M | $103.0 M | $356.1 M |
| [Comilla](Comilla/README.md) | 600,000 | 114 | $444.4 M | $110.3 M | $334.1 M |
| [Barisal](Barisal/README.md) | 550,000 | 130 | $534.6 M | $128.7 M | $405.8 M |

## Local Basis And Regeneration

Country finance parameters use `BD` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 scripts/generate-national-briefs.py
```
