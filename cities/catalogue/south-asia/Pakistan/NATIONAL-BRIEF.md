# Pakistan National OpenSourceRail Strategy

This page contains only Pakistan-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$80.70 B (90.0%) of external capital** and **$101.16 B of external interest**. Capital plus saved interest totals **$181.86 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 13 |
| Represented population | 37,603,000 |
| Trainsets / vehicle modules | 2,641 / 11,649 |
| City infrastructure and fleet CAPEX | $48.92 B |
| Shared national factory | $838.0 M |
| Factory sizing basis | 4,200 modules for Karachi, then reused nationally |
| **Total national programme** | **$49.82 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $8.97 B (18.0%) |
| Domestic / local capital | $40.84 B (82.0%) |
| Annual external capital draw | $1.28 B / yr |
| Annual local capital draw | $5.83 B / yr |
| Annual public construction commitment | $6.96 B / yr for 7 years |
| Annual post-grace debt service | $5.95 B / yr |
| Default foreign-turnkey external capital | $89.67 B |
| External capital saved | $80.70 B |
| Capital + lifetime external interest saved | $181.86 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $36.03 B | $5.40 B | $30.63 B |
| Stations | $3.61 B | $722.6 M | $2.89 B |
| Depots | $1.19 B | $296.9 M | $890.8 M |
| Rolling stock | $3.31 B | $1.16 B | $2.15 B |
| Dedicated solar plants | $1.40 B | $631.0 M | $771.2 M |
| Residual train control | $77.7 M | $38.8 M | $38.8 M |
| Charging microgrids | $187.8 M | $75.1 M | $112.7 M |
| EPC / project services | $3.17 B | $475.1 M | $2.69 B |
| Shared national trainset factory | $838.0 M | $167.6 M | $670.4 M |
| **Total** | **$49.82 B** | **$8.97 B** | **$40.84 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Karachi](Karachi/README.md) | 20,300,000 | 700 | $26.23 B | $4.46 B | $21.77 B |
| [Faisalabad](Faisalabad/README.md) | 3,556,000 | 245 | $2.74 B | $588.8 M | $2.15 B |
| [Gujranwala](Gujranwala/README.md) | 2,300,000 | 213 | $2.51 B | $499.2 M | $2.01 B |
| [Peshawar](Peshawar/README.md) | 2,300,000 | 215 | $2.78 B | $537.9 M | $2.24 B |
| [Multan](Multan/README.md) | 2,197,000 | 140 | $1.63 B | $321.8 M | $1.31 B |
| [Hyderabad Pk](Hyderabad-Pk/README.md) | 1,900,000 | 210 | $3.10 B | $584.3 M | $2.52 B |
| [Quetta](Quetta/README.md) | 1,200,000 | 113 | $4.82 B | $786.2 M | $4.03 B |
| [Bahawalpur](Bahawalpur/README.md) | 900,000 | 120 | $653.1 M | $135.6 M | $517.6 M |
| [Sialkot](Sialkot/README.md) | 750,000 | 165 | $1.18 B | $228.2 M | $951.1 M |
| [Sheikhupura](Sheikhupura/README.md) | 600,000 | 118 | $603.3 M | $130.3 M | $473.1 M |
| [Sukkur](Sukkur/README.md) | 600,000 | 130 | $997.2 M | $190.1 M | $807.1 M |
| [Larkana](Larkana/README.md) | 500,000 | 107 | $762.5 M | $147.0 M | $615.5 M |
| [Rahim Yar Khan](Rahim-Yar-Khan/README.md) | 500,000 | 165 | $913.5 M | $189.2 M | $724.3 M |

## Local Basis And Regeneration

Country finance parameters use `PK` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
