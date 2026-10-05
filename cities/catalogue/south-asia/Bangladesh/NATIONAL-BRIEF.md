# Bangladesh National OpenSourceRail Strategy

This page contains only Bangladesh-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$31.52 B (88.3%) of external capital** and **$39.51 B of external interest**. Capital plus saved interest totals **$71.03 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 10 |
| Represented population | 13,550,000 |
| Trainsets / vehicle modules | 2,161 / 8,674 |
| City infrastructure and fleet CAPEX | $18.90 B |
| Shared national factory | $861.2 M |
| Factory sizing basis | 3,138 modules for Chittagong, then reused nationally |
| **Total national programme** | **$19.82 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $4.16 B (21.0%) |
| Domestic / local capital | $15.66 B (79.0%) |
| Annual external capital draw | $595.0 M / yr |
| Annual local capital draw | $2.24 B / yr |
| Annual public construction commitment | $1.70 B / yr for 7 years |
| Annual post-grace debt service | $1.39 B / yr |
| Default foreign-turnkey external capital | $35.68 B |
| External capital saved | $31.52 B |
| Capital + lifetime external interest saved | $71.03 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $10.57 B | $1.59 B | $8.98 B |
| Stations | $2.32 B | $463.7 M | $1.85 B |
| Depots | $881.8 M | $220.5 M | $661.4 M |
| Rolling stock | $2.49 B | $871.4 M | $1.62 B |
| Dedicated solar plants | $1.33 B | $599.3 M | $732.5 M |
| Residual train control | $54.5 M | $27.2 M | $27.2 M |
| Charging microgrids | $109.5 M | $43.8 M | $65.7 M |
| EPC / project services | $1.21 B | $181.5 M | $1.03 B |
| Shared national trainset factory | $861.2 M | $172.2 M | $688.9 M |
| **Total** | **$19.82 B** | **$4.16 B** | **$15.66 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Chittagong](Chittagong/README.md) | 5,200,000 | 523 | $6.01 B | $1.33 B | $4.68 B |
| [Khulna](Khulna/README.md) | 1,500,000 | 280 | $3.53 B | $701.2 M | $2.83 B |
| [Gazipur](Gazipur/README.md) | 1,400,000 | 342 | $3.65 B | $761.5 M | $2.89 B |
| [Narayanganj](Narayanganj/README.md) | 950,000 | 229 | $1.30 B | $269.5 M | $1.03 B |
| [Rajshahi](Rajshahi/README.md) | 950,000 | 104 | $571.9 M | $120.4 M | $451.6 M |
| [Sylhet](Sylhet/README.md) | 900,000 | 131 | $700.2 M | $148.0 M | $552.2 M |
| [Rangpur](Rangpur/README.md) | 800,000 | 120 | $659.6 M | $138.3 M | $521.3 M |
| [Mymensingh](Mymensingh/README.md) | 700,000 | 118 | $715.1 M | $146.2 M | $568.9 M |
| [Comilla](Comilla/README.md) | 600,000 | 139 | $768.9 M | $160.6 M | $608.2 M |
| [Barisal](Barisal/README.md) | 550,000 | 175 | $1.01 B | $209.0 M | $799.9 M |

## Local Basis And Regeneration

Country finance parameters use `BD` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
