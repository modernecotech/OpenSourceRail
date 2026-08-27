# Pakistan National OpenSourceRail Strategy

This page contains only Pakistan-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$24.66 B (86.7%) of external capital** and **$30.91 B of external interest**. Capital plus saved interest totals **$55.57 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 13 |
| Represented population | 37,603,000 |
| Trainsets / vehicle modules | 2,461 / 11,191 |
| City infrastructure and fleet CAPEX | $15.53 B |
| Shared national factory | $254.5 M |
| Factory sizing basis | 4,242 modules for Karachi, then reused nationally |
| **Total national programme** | **$15.80 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $3.79 B (24.0%) |
| Domestic / local capital | $12.02 B (76.0%) |
| Annual external capital draw | $541.3 M / yr |
| Annual local capital draw | $1.72 B / yr |
| Annual public construction commitment | $2.10 B / yr for 7 years |
| Annual post-grace debt service | $1.82 B / yr |
| Default foreign-turnkey external capital | $28.45 B |
| External capital saved | $24.66 B |
| Capital + lifetime external interest saved | $55.57 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $6.17 B | $926.0 M | $5.25 B |
| Stations | $3.16 B | $631.6 M | $2.53 B |
| Depots | $104.0 M | $26.0 M | $78.0 M |
| Rolling stock | $3.17 B | $1.11 B | $2.06 B |
| Dedicated solar plants | $1.77 B | $796.1 M | $973.0 M |
| Residual train control | $83.7 M | $41.8 M | $41.8 M |
| Charging microgrids | $176.0 M | $70.4 M | $105.6 M |
| EPC / project services | $918.2 M | $137.7 M | $780.5 M |
| Shared national trainset factory | $254.5 M | $50.9 M | $203.6 M |
| **Total** | **$15.80 B** | **$3.79 B** | **$12.02 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Karachi](Karachi/README.md) | 20,300,000 | 707 | $4.41 B | $1.15 B | $3.25 B |
| [Faisalabad](Faisalabad/README.md) | 3,556,000 | 252 | $1.77 B | $448.1 M | $1.32 B |
| [Gujranwala](Gujranwala/README.md) | 2,300,000 | 218 | $1.43 B | $338.4 M | $1.09 B |
| [Peshawar](Peshawar/README.md) | 2,300,000 | 221 | $1.56 B | $359.3 M | $1.20 B |
| [Multan](Multan/README.md) | 2,197,000 | 149 | $1.17 B | $262.5 M | $912.3 M |
| [Hyderabad Pk](Hyderabad-Pk/README.md) | 1,900,000 | 216 | $1.60 B | $366.2 M | $1.24 B |
| [Quetta](Quetta/README.md) | 1,200,000 | 127 | $1.00 B | $226.3 M | $774.9 M |
| [Bahawalpur](Bahawalpur/README.md) | 900,000 | 100 | $402.8 M | $95.4 M | $307.3 M |
| [Sialkot](Sialkot/README.md) | 750,000 | 134 | $700.4 M | $149.4 M | $551.0 M |
| [Sheikhupura](Sheikhupura/README.md) | 600,000 | 37 | $180.8 M | $40.4 M | $140.4 M |
| [Sukkur](Sukkur/README.md) | 600,000 | 92 | $529.7 M | $111.0 M | $418.7 M |
| [Larkana](Larkana/README.md) | 500,000 | 79 | $333.5 M | $76.7 M | $256.8 M |
| [Rahim Yar Khan](Rahim-Yar-Khan/README.md) | 500,000 | 129 | $440.9 M | $108.4 M | $332.5 M |

## Local Basis And Regeneration

Country finance parameters use `PK` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 scripts/generate-national-briefs.py
```
