# India National OpenSourceRail Strategy

This page contains only India-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$217.50 B (90.2%) of external capital** and **$267.41 B of external interest**. Capital plus saved interest totals **$484.90 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 17 |
| Represented population | 36,304,000 |
| Trainsets / vehicle modules | 5,272 / 25,198 |
| City infrastructure and fleet CAPEX | $133.05 B |
| Shared national factory | $854.7 M |
| Factory sizing basis | 3,198 modules for Kanpur, then reused nationally |
| **Total national programme** | **$133.97 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $23.65 B (17.6%) |
| Domestic / local capital | $110.32 B (82.4%) |
| Annual external capital draw | $4.73 B / yr |
| Annual local capital draw | $22.06 B / yr |
| Annual public construction commitment | $11.83 B / yr for 5 years |
| Annual post-grace debt service | $8.32 B / yr |
| Default foreign-turnkey external capital | $241.14 B |
| External capital saved | $217.50 B |
| Capital + lifetime external interest saved | $484.90 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $101.46 B | $15.22 B | $86.24 B |
| Stations | $8.97 B | $1.79 B | $7.18 B |
| Depots | $2.39 B | $597.7 M | $1.79 B |
| Rolling stock | $7.06 B | $2.47 B | $4.59 B |
| Dedicated solar plants | $4.09 B | $1.84 B | $2.25 B |
| Residual train control | $181.1 M | $90.5 M | $90.5 M |
| Charging microgrids | $467.5 M | $187.0 M | $280.5 M |
| EPC / project services | $8.50 B | $1.27 B | $7.22 B |
| Shared national trainset factory | $854.7 M | $170.9 M | $683.8 M |
| **Total** | **$133.97 B** | **$23.65 B** | **$110.32 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Lucknow](Lucknow/README.md) | 3,500,000 | 507 | $5.61 B | $1.22 B | $4.39 B |
| [Indore](Indore/README.md) | 3,200,000 | 516 | $5.49 B | $1.21 B | $4.28 B |
| [Kanpur](Kanpur/README.md) | 3,200,000 | 533 | $28.58 B | $4.70 B | $23.88 B |
| [Coimbatore](Coimbatore/README.md) | 3,084,000 | 499 | $5.61 B | $1.26 B | $4.35 B |
| [Patna](Patna/README.md) | 2,520,000 | 618 | $36.43 B | $5.84 B | $30.60 B |
| [Bhopal](Bhopal/README.md) | 2,400,000 | 225 | $7.48 B | $1.25 B | $6.23 B |
| [Visakhapatnam](Visakhapatnam/README.md) | 2,300,000 | 276 | $3.30 B | $670.2 M | $2.63 B |
| [Vadodara](Vadodara/README.md) | 2,200,000 | 195 | $2.00 B | $405.7 M | $1.60 B |
| [Rajkot](Rajkot/README.md) | 1,800,000 | 155 | $5.43 B | $901.9 M | $4.53 B |
| [Agra](Agra/README.md) | 1,700,000 | 182 | $2.36 B | $458.2 M | $1.90 B |
| [Madurai](Madurai/README.md) | 1,600,000 | 262 | $9.41 B | $1.58 B | $7.83 B |
| [Meerut](Meerut/README.md) | 1,600,000 | 150 | $1.93 B | $377.7 M | $1.55 B |
| [Raipur](Raipur/README.md) | 1,500,000 | 202 | $2.16 B | $445.0 M | $1.71 B |
| [Varanasi](Varanasi/README.md) | 1,500,000 | 252 | $6.87 B | $1.17 B | $5.70 B |
| [Vijayawada](Vijayawada/README.md) | 1,500,000 | 245 | $4.40 B | $816.8 M | $3.58 B |
| [Ranchi](Ranchi/README.md) | 1,400,000 | 264 | $3.17 B | $641.7 M | $2.53 B |
| [Jodhpur](Jodhpur/README.md) | 1,300,000 | 191 | $2.82 B | $531.7 M | $2.29 B |

## Local Basis And Regeneration

Country finance parameters use `IN` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
