# India National OpenSourceRail Strategy

This page contains only India-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$54.49 B (86.3%) of external capital** and **$66.99 B of external interest**. Capital plus saved interest totals **$121.48 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 17 |
| Represented population | 36,304,000 |
| Trainsets / vehicle modules | 5,084 / 24,736 |
| City infrastructure and fleet CAPEX | $34.85 B |
| Shared national factory | $205.6 M |
| Factory sizing basis | 3,426 modules for Indore, then reused nationally |
| **Total national programme** | **$35.07 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $8.63 B (24.6%) |
| Domestic / local capital | $26.43 B (75.4%) |
| Annual external capital draw | $1.73 B / yr |
| Annual local capital draw | $5.29 B / yr |
| Annual public construction commitment | $2.97 B / yr for 5 years |
| Annual post-grace debt service | $2.16 B / yr |
| Default foreign-turnkey external capital | $63.12 B |
| External capital saved | $54.49 B |
| Capital + lifetime external interest saved | $121.48 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $13.55 B | $2.03 B | $11.52 B |
| Stations | $6.82 B | $1.36 B | $5.46 B |
| Depots | $136.0 M | $34.0 M | $102.0 M |
| Rolling stock | $6.93 B | $2.42 B | $4.50 B |
| Dedicated solar plants | $4.85 B | $2.18 B | $2.67 B |
| Residual train control | $190.3 M | $95.1 M | $95.1 M |
| Charging microgrids | $407.2 M | $162.9 M | $244.3 M |
| EPC / project services | $1.98 B | $296.5 M | $1.68 B |
| Shared national trainset factory | $205.6 M | $41.1 M | $164.4 M |
| **Total** | **$35.07 B** | **$8.63 B** | **$26.43 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Lucknow](Lucknow/README.md) | 3,500,000 | 556 | $3.58 B | $939.5 M | $2.65 B |
| [Indore](Indore/README.md) | 3,200,000 | 571 | $3.47 B | $925.7 M | $2.55 B |
| [Kanpur](Kanpur/README.md) | 3,200,000 | 533 | $3.40 B | $895.7 M | $2.51 B |
| [Coimbatore](Coimbatore/README.md) | 3,084,000 | 540 | $3.75 B | $994.3 M | $2.76 B |
| [Patna](Patna/README.md) | 2,520,000 | 215 | $1.75 B | $399.1 M | $1.36 B |
| [Bhopal](Bhopal/README.md) | 2,400,000 | 245 | $1.79 B | $411.1 M | $1.37 B |
| [Visakhapatnam](Visakhapatnam/README.md) | 2,300,000 | 286 | $2.05 B | $489.0 M | $1.56 B |
| [Vadodara](Vadodara/README.md) | 2,200,000 | 207 | $1.40 B | $328.1 M | $1.07 B |
| [Rajkot](Rajkot/README.md) | 1,800,000 | 162 | $1.14 B | $262.4 M | $881.0 M |
| [Agra](Agra/README.md) | 1,700,000 | 187 | $1.42 B | $322.8 M | $1.10 B |
| [Madurai](Madurai/README.md) | 1,600,000 | 268 | $1.71 B | $422.8 M | $1.29 B |
| [Meerut](Meerut/README.md) | 1,600,000 | 158 | $1.18 B | $270.6 M | $906.1 M |
| [Raipur](Raipur/README.md) | 1,500,000 | 212 | $1.27 B | $316.8 M | $950.7 M |
| [Varanasi](Varanasi/README.md) | 1,500,000 | 243 | $1.72 B | $393.2 M | $1.33 B |
| [Vijayawada](Vijayawada/README.md) | 1,500,000 | 266 | $1.81 B | $440.2 M | $1.37 B |
| [Ranchi](Ranchi/README.md) | 1,400,000 | 260 | $1.87 B | $447.5 M | $1.42 B |
| [Jodhpur](Jodhpur/README.md) | 1,300,000 | 175 | $1.54 B | $331.6 M | $1.21 B |

## Local Basis And Regeneration

Country finance parameters use `IN` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
