# Bangladesh National OpenSourceRail Strategy

This page contains only Bangladesh-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$49.89 B (89.5%) of external capital** and **$62.54 B of external interest**. Capital plus saved interest totals **$112.43 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 10 |
| Represented population | 13,550,000 |
| Trainsets / vehicle modules | 2,161 / 8,674 |
| City infrastructure and fleet CAPEX | $30.04 B |
| Shared national factory | $861.2 M |
| Factory sizing basis | 3,138 modules for Chittagong, then reused nationally |
| **Total national programme** | **$30.96 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $5.83 B (18.8%) |
| Domestic / local capital | $25.12 B (81.2%) |
| Annual external capital draw | $833.5 M / yr |
| Annual local capital draw | $3.59 B / yr |
| Annual public construction commitment | $2.69 B / yr for 7 years |
| Annual post-grace debt service | $2.18 B / yr |
| Default foreign-turnkey external capital | $55.72 B |
| External capital saved | $49.89 B |
| Capital + lifetime external interest saved | $112.43 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $20.97 B | $3.15 B | $17.83 B |
| Stations | $2.32 B | $463.7 M | $1.85 B |
| Depots | $881.8 M | $220.5 M | $661.4 M |
| Rolling stock | $2.49 B | $871.4 M | $1.62 B |
| Dedicated solar plants | $1.33 B | $599.3 M | $732.5 M |
| Residual train control | $54.5 M | $27.2 M | $27.2 M |
| Charging microgrids | $109.5 M | $43.8 M | $65.7 M |
| EPC / project services | $1.94 B | $290.7 M | $1.65 B |
| Shared national trainset factory | $861.2 M | $172.2 M | $688.9 M |
| **Total** | **$30.96 B** | **$5.83 B** | **$25.12 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Chittagong](Chittagong/README.md) | 5,200,000 | 523 | $12.85 B | $2.35 B | $10.49 B |
| [Khulna](Khulna/README.md) | 1,500,000 | 280 | $7.19 B | $1.25 B | $5.94 B |
| [Gazipur](Gazipur/README.md) | 1,400,000 | 342 | $4.15 B | $836.8 M | $3.31 B |
| [Narayanganj](Narayanganj/README.md) | 950,000 | 229 | $1.40 B | $284.4 M | $1.11 B |
| [Rajshahi](Rajshahi/README.md) | 950,000 | 104 | $573.2 M | $120.6 M | $452.6 M |
| [Sylhet](Sylhet/README.md) | 900,000 | 131 | $709.9 M | $149.5 M | $560.4 M |
| [Rangpur](Rangpur/README.md) | 800,000 | 120 | $659.6 M | $138.3 M | $521.3 M |
| [Mymensingh](Mymensingh/README.md) | 700,000 | 118 | $715.1 M | $146.1 M | $568.9 M |
| [Comilla](Comilla/README.md) | 600,000 | 139 | $769.2 M | $160.7 M | $608.5 M |
| [Barisal](Barisal/README.md) | 550,000 | 175 | $1.03 B | $212.6 M | $820.3 M |

## Local Basis And Regeneration

Country finance parameters use `BD` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
