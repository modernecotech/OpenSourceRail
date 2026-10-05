# Cameroon National OpenSourceRail Strategy

This page contains only Cameroon-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$19.82 B (88.1%) of external capital** and **$24.85 B of external interest**. Capital plus saved interest totals **$44.67 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 10 |
| Represented population | 11,650,000 |
| Trainsets / vehicle modules | 1,410 / 5,944 |
| City infrastructure and fleet CAPEX | $11.44 B |
| Shared national factory | $990.6 M |
| Factory sizing basis | 1,776 modules for Douala, then reused nationally |
| **Total national programme** | **$12.50 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $2.67 B (21.4%) |
| Domestic / local capital | $9.83 B (78.6%) |
| Annual external capital draw | $381.2 M / yr |
| Annual local capital draw | $1.40 B / yr |
| Annual public construction commitment | $1.07 B / yr for 7 years |
| Annual post-grace debt service | $873.6 M / yr |
| Default foreign-turnkey external capital | $22.49 B |
| External capital saved | $19.82 B |
| Capital + lifetime external interest saved | $44.67 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $6.25 B | $937.1 M | $5.31 B |
| Stations | $1.21 B | $242.5 M | $969.8 M |
| Depots | $642.6 M | $160.7 M | $482.0 M |
| Rolling stock | $1.71 B | $599.6 M | $1.11 B |
| Dedicated solar plants | $834.4 M | $375.5 M | $458.9 M |
| Residual train control | $32.2 M | $16.1 M | $16.1 M |
| Charging microgrids | $60.2 M | $24.1 M | $36.1 M |
| EPC / project services | $762.9 M | $114.4 M | $648.5 M |
| Shared national trainset factory | $990.6 M | $198.1 M | $792.5 M |
| **Total** | **$12.50 B** | **$2.67 B** | **$9.83 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Yaounde](Yaounde/README.md) | 4,100,000 | 281 | $3.15 B | $705.1 M | $2.45 B |
| [Douala](Douala/README.md) | 3,900,000 | 296 | $3.63 B | $789.5 M | $2.84 B |
| [Bafoussam](Bafoussam/README.md) | 600,000 | 187 | $936.9 M | $201.9 M | $735.0 M |
| [Bamenda](Bamenda/README.md) | 600,000 | 134 | $708.9 M | $150.9 M | $558.1 M |
| [Garoua](Garoua/README.md) | 600,000 | 82 | $532.5 M | $105.0 M | $427.5 M |
| [Maroua](Maroua/README.md) | 500,000 | 148 | $829.5 M | $169.0 M | $660.5 M |
| [Kumba](Kumba/README.md) | 400,000 | 113 | $634.0 M | $133.2 M | $500.8 M |
| [Bertoua](Bertoua/README.md) | 350,000 | 78 | $448.0 M | $92.9 M | $355.1 M |
| [Ngaoundere](Ngaoundere/README.md) | 350,000 | 74 | $444.3 M | $89.6 M | $354.7 M |
| [Edea](Edea/README.md) | 250,000 | 17 | $120.7 M | $22.6 M | $98.1 M |

## Local Basis And Regeneration

Country finance parameters use `CM` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
