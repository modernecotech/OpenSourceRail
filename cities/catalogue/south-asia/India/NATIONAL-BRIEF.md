# India National OpenSourceRail Strategy

This page contains only India-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$86.09 B (88.6%) of external capital** and **$105.85 B of external interest**. Capital plus saved interest totals **$191.94 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 17 |
| Represented population | 36,304,000 |
| Trainsets / vehicle modules | 4,505 / 21,780 |
| City infrastructure and fleet CAPEX | $53.13 B |
| Shared national factory | $815.5 M |
| Factory sizing basis | 2,922 modules for Indore, then reused nationally |
| **Total national programme** | **$54.01 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $11.12 B (20.6%) |
| Domestic / local capital | $42.89 B (79.4%) |
| Annual external capital draw | $2.22 B / yr |
| Annual local capital draw | $8.58 B / yr |
| Annual public construction commitment | $4.69 B / yr for 5 years |
| Annual post-grace debt service | $3.34 B / yr |
| Default foreign-turnkey external capital | $97.21 B |
| External capital saved | $86.09 B |
| Capital + lifetime external interest saved | $191.94 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $32.28 B | $4.84 B | $27.44 B |
| Stations | $4.99 B | $997.3 M | $3.99 B |
| Depots | $2.22 B | $555.8 M | $1.67 B |
| Rolling stock | $6.10 B | $2.13 B | $3.96 B |
| Dedicated solar plants | $3.82 B | $1.72 B | $2.10 B |
| Residual train control | $166.4 M | $83.2 M | $83.2 M |
| Charging microgrids | $329.9 M | $132.0 M | $198.0 M |
| EPC / project services | $3.28 B | $492.4 M | $2.79 B |
| Shared national trainset factory | $815.5 M | $163.1 M | $652.4 M |
| **Total** | **$54.01 B** | **$11.12 B** | **$42.89 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Lucknow](Lucknow/README.md) | 3,500,000 | 478 | $5.37 B | $1.16 B | $4.21 B |
| [Indore](Indore/README.md) | 3,200,000 | 487 | $5.16 B | $1.13 B | $4.03 B |
| [Kanpur](Kanpur/README.md) | 3,200,000 | 456 | $5.09 B | $1.10 B | $3.99 B |
| [Coimbatore](Coimbatore/README.md) | 3,084,000 | 459 | $5.03 B | $1.13 B | $3.90 B |
| [Patna](Patna/README.md) | 2,520,000 | 199 | $2.74 B | $536.8 M | $2.21 B |
| [Bhopal](Bhopal/README.md) | 2,400,000 | 207 | $2.47 B | $487.1 M | $1.98 B |
| [Visakhapatnam](Visakhapatnam/README.md) | 2,300,000 | 265 | $3.08 B | $627.8 M | $2.45 B |
| [Vadodara](Vadodara/README.md) | 2,200,000 | 172 | $1.77 B | $355.6 M | $1.41 B |
| [Rajkot](Rajkot/README.md) | 1,800,000 | 143 | $1.88 B | $362.5 M | $1.52 B |
| [Agra](Agra/README.md) | 1,700,000 | 176 | $2.29 B | $443.2 M | $1.84 B |
| [Madurai](Madurai/README.md) | 1,600,000 | 247 | $2.94 B | $593.1 M | $2.35 B |
| [Meerut](Meerut/README.md) | 1,600,000 | 138 | $1.84 B | $357.1 M | $1.48 B |
| [Raipur](Raipur/README.md) | 1,500,000 | 196 | $2.09 B | $429.4 M | $1.66 B |
| [Varanasi](Varanasi/README.md) | 1,500,000 | 225 | $3.01 B | $578.5 M | $2.44 B |
| [Vijayawada](Vijayawada/README.md) | 1,500,000 | 240 | $2.82 B | $571.2 M | $2.25 B |
| [Ranchi](Ranchi/README.md) | 1,400,000 | 246 | $3.02 B | $608.9 M | $2.42 B |
| [Jodhpur](Jodhpur/README.md) | 1,300,000 | 171 | $2.53 B | $475.1 M | $2.05 B |

## Local Basis And Regeneration

Country finance parameters use `IN` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
