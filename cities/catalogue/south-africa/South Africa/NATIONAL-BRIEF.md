# South Africa National OpenSourceRail Strategy

This page contains only South Africa-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$14.53 B (87.9%) of external capital** and **$17.86 B of external interest**. Capital plus saved interest totals **$32.39 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 5 |
| Represented population | 6,200,000 |
| Trainsets / vehicle modules | 1,061 / 4,669 |
| City infrastructure and fleet CAPEX | $8.61 B |
| Shared national factory | $537.4 M |
| Factory sizing basis | 3,096 modules for Durban, then reused nationally |
| **Total national programme** | **$9.19 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $2.00 B (21.8%) |
| Domestic / local capital | $7.18 B (78.2%) |
| Annual external capital draw | $400.9 M / yr |
| Annual local capital draw | $1.44 B / yr |
| Annual public construction commitment | $980.7 M / yr for 5 years |
| Annual post-grace debt service | $736.9 M / yr |
| Default foreign-turnkey external capital | $16.53 B |
| External capital saved | $14.53 B |
| Capital + lifetime external interest saved | $32.39 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $4.71 B | $706.7 M | $4.00 B |
| Stations | $758.1 M | $151.6 M | $606.5 M |
| Depots | $457.7 M | $114.4 M | $343.2 M |
| Rolling stock | $1.34 B | $467.7 M | $868.6 M |
| Dedicated solar plants | $759.5 M | $341.8 M | $417.7 M |
| Residual train control | $26.2 M | $13.1 M | $13.1 M |
| Charging microgrids | $47.9 M | $19.2 M | $28.7 M |
| EPC / project services | $551.2 M | $82.7 M | $468.6 M |
| Shared national trainset factory | $537.4 M | $107.5 M | $429.9 M |
| **Total** | **$9.19 B** | **$2.00 B** | **$7.18 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Durban](Durban/README.md) | 3,900,000 | 516 | $5.68 B | $1.28 B | $4.40 B |
| [East London Za](East-London-Za/README.md) | 800,000 | 179 | $899.2 M | $195.7 M | $703.5 M |
| [Bloemfontein](Bloemfontein/README.md) | 600,000 | 175 | $887.4 M | $192.6 M | $694.8 M |
| [Polokwane](Polokwane/README.md) | 600,000 | 129 | $666.8 M | $138.3 M | $528.5 M |
| [Nelspruit](Nelspruit/README.md) | 300,000 | 62 | $476.8 M | $88.0 M | $388.8 M |

## Local Basis And Regeneration

Country finance parameters use `ZA` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
