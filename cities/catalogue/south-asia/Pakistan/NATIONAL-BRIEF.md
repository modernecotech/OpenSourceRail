# Pakistan National OpenSourceRail Strategy

This page contains only Pakistan-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$40.01 B (88.7%) of external capital** and **$50.15 B of external interest**. Capital plus saved interest totals **$90.16 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 13 |
| Represented population | 37,603,000 |
| Trainsets / vehicle modules | 2,409 / 10,588 |
| City infrastructure and fleet CAPEX | $24.21 B |
| Shared national factory | $790.6 M |
| Factory sizing basis | 3,618 modules for Karachi, then reused nationally |
| **Total national programme** | **$25.05 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $5.09 B (20.3%) |
| Domestic / local capital | $19.96 B (79.7%) |
| Annual external capital draw | $727.3 M / yr |
| Annual local capital draw | $2.85 B / yr |
| Annual public construction commitment | $3.43 B / yr for 7 years |
| Annual post-grace debt service | $2.95 B / yr |
| Default foreign-turnkey external capital | $45.10 B |
| External capital saved | $40.01 B |
| Capital + lifetime external interest saved | $90.16 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $14.85 B | $2.23 B | $12.62 B |
| Stations | $2.14 B | $427.0 M | $1.71 B |
| Depots | $1.14 B | $284.9 M | $854.6 M |
| Rolling stock | $3.01 B | $1.05 B | $1.96 B |
| Dedicated solar plants | $1.37 B | $615.4 M | $752.1 M |
| Residual train control | $74.3 M | $37.1 M | $37.1 M |
| Charging microgrids | $139.8 M | $55.9 M | $83.9 M |
| EPC / project services | $1.55 B | $232.4 M | $1.32 B |
| Shared national trainset factory | $790.6 M | $158.1 M | $632.5 M |
| **Total** | **$25.05 B** | **$5.09 B** | **$19.96 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Karachi](Karachi/README.md) | 20,300,000 | 603 | $6.23 B | $1.36 B | $4.87 B |
| [Faisalabad](Faisalabad/README.md) | 3,556,000 | 232 | $2.59 B | $554.9 M | $2.04 B |
| [Gujranwala](Gujranwala/README.md) | 2,300,000 | 207 | $2.34 B | $466.7 M | $1.87 B |
| [Peshawar](Peshawar/README.md) | 2,300,000 | 205 | $2.54 B | $495.7 M | $2.04 B |
| [Multan](Multan/README.md) | 2,197,000 | 128 | $1.54 B | $300.4 M | $1.24 B |
| [Hyderabad Pk](Hyderabad-Pk/README.md) | 1,900,000 | 200 | $3.00 B | $562.0 M | $2.44 B |
| [Quetta](Quetta/README.md) | 1,200,000 | 116 | $1.53 B | $295.2 M | $1.24 B |
| [Bahawalpur](Bahawalpur/README.md) | 900,000 | 116 | $602.6 M | $125.6 M | $477.0 M |
| [Sialkot](Sialkot/README.md) | 750,000 | 163 | $1.14 B | $220.1 M | $918.4 M |
| [Sheikhupura](Sheikhupura/README.md) | 600,000 | 51 | $299.8 M | $61.2 M | $238.6 M |
| [Sukkur](Sukkur/README.md) | 600,000 | 124 | $857.7 M | $165.4 M | $692.3 M |
| [Larkana](Larkana/README.md) | 500,000 | 107 | $746.6 M | $144.5 M | $602.1 M |
| [Rahim Yar Khan](Rahim-Yar-Khan/README.md) | 500,000 | 157 | $799.2 M | $168.1 M | $631.1 M |

## Local Basis And Regeneration

Country finance parameters use `PK` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
