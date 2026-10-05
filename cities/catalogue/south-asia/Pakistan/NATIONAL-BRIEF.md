# Pakistan National OpenSourceRail Strategy

This page contains only Pakistan-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$43.54 B (88.6%) of external capital** and **$54.58 B of external interest**. Capital plus saved interest totals **$98.12 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 13 |
| Represented population | 37,603,000 |
| Trainsets / vehicle modules | 2,641 / 11,649 |
| City infrastructure and fleet CAPEX | $26.40 B |
| Shared national factory | $838.0 M |
| Factory sizing basis | 4,200 modules for Karachi, then reused nationally |
| **Total national programme** | **$27.30 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $5.59 B (20.5%) |
| Domestic / local capital | $21.70 B (79.5%) |
| Annual external capital draw | $798.9 M / yr |
| Annual local capital draw | $3.10 B / yr |
| Annual public construction commitment | $3.74 B / yr for 7 years |
| Annual post-grace debt service | $3.21 B / yr |
| Default foreign-turnkey external capital | $49.13 B |
| External capital saved | $43.54 B |
| Capital + lifetime external interest saved | $98.12 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $14.99 B | $2.25 B | $12.74 B |
| Stations | $3.61 B | $722.6 M | $2.89 B |
| Depots | $1.19 B | $296.9 M | $890.8 M |
| Rolling stock | $3.31 B | $1.16 B | $2.15 B |
| Dedicated solar plants | $1.40 B | $631.0 M | $771.2 M |
| Residual train control | $77.7 M | $38.8 M | $38.8 M |
| Charging microgrids | $187.8 M | $75.1 M | $112.7 M |
| EPC / project services | $1.69 B | $254.1 M | $1.44 B |
| Shared national trainset factory | $838.0 M | $167.6 M | $670.4 M |
| **Total** | **$27.30 B** | **$5.59 B** | **$21.70 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Karachi](Karachi/README.md) | 20,300,000 | 700 | $7.90 B | $1.71 B | $6.20 B |
| [Faisalabad](Faisalabad/README.md) | 3,556,000 | 245 | $2.74 B | $588.8 M | $2.15 B |
| [Gujranwala](Gujranwala/README.md) | 2,300,000 | 213 | $2.43 B | $487.4 M | $1.95 B |
| [Peshawar](Peshawar/README.md) | 2,300,000 | 215 | $2.63 B | $515.5 M | $2.11 B |
| [Multan](Multan/README.md) | 2,197,000 | 140 | $1.63 B | $321.8 M | $1.31 B |
| [Hyderabad Pk](Hyderabad-Pk/README.md) | 1,900,000 | 210 | $2.58 B | $505.8 M | $2.07 B |
| [Quetta](Quetta/README.md) | 1,200,000 | 113 | $1.49 B | $288.0 M | $1.21 B |
| [Bahawalpur](Bahawalpur/README.md) | 900,000 | 120 | $653.1 M | $135.6 M | $517.6 M |
| [Sialkot](Sialkot/README.md) | 750,000 | 165 | $1.18 B | $228.2 M | $951.1 M |
| [Sheikhupura](Sheikhupura/README.md) | 600,000 | 118 | $603.3 M | $130.3 M | $473.1 M |
| [Sukkur](Sukkur/README.md) | 600,000 | 130 | $937.8 M | $181.2 M | $756.6 M |
| [Larkana](Larkana/README.md) | 500,000 | 107 | $762.3 M | $147.0 M | $615.4 M |
| [Rahim Yar Khan](Rahim-Yar-Khan/README.md) | 500,000 | 165 | $848.7 M | $179.4 M | $669.2 M |

## Local Basis And Regeneration

Country finance parameters use `PK` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
