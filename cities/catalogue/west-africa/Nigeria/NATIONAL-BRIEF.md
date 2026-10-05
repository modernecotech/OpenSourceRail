# Nigeria National OpenSourceRail Strategy

This page contains only Nigeria-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$56.78 B (89.6%) of external capital** and **$71.18 B of external interest**. Capital plus saved interest totals **$127.96 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 10 |
| Represented population | 19,200,000 |
| Trainsets / vehicle modules | 2,061 / 9,547 |
| City infrastructure and fleet CAPEX | $34.44 B |
| Shared national factory | $697.0 M |
| Factory sizing basis | 4,068 modules for Kano, then reused nationally |
| **Total national programme** | **$35.19 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $6.56 B (18.6%) |
| Domestic / local capital | $28.63 B (81.4%) |
| Annual external capital draw | $936.5 M / yr |
| Annual local capital draw | $4.09 B / yr |
| Annual public construction commitment | $4.21 B / yr for 7 years |
| Annual post-grace debt service | $3.53 B / yr |
| Default foreign-turnkey external capital | $63.33 B |
| External capital saved | $56.78 B |
| Capital + lifetime external interest saved | $127.96 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $24.42 B | $3.66 B | $20.76 B |
| Stations | $2.59 B | $517.1 M | $2.07 B |
| Depots | $968.2 M | $242.1 M | $726.2 M |
| Rolling stock | $2.70 B | $944.4 M | $1.75 B |
| Dedicated solar plants | $1.39 B | $626.6 M | $765.9 M |
| Residual train control | $63.6 M | $31.8 M | $31.8 M |
| Charging microgrids | $146.8 M | $58.7 M | $88.1 M |
| EPC / project services | $2.21 B | $331.6 M | $1.88 B |
| Shared national trainset factory | $697.0 M | $139.4 M | $557.6 M |
| **Total** | **$35.19 B** | **$6.56 B** | **$28.63 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Kano](Kano/README.md) | 4,200,000 | 678 | $7.85 B | $1.66 B | $6.19 B |
| [Ibadan](Ibadan/README.md) | 3,900,000 | 182 | $2.01 B | $448.5 M | $1.56 B |
| [Port Harcourt](Port-Harcourt/README.md) | 3,000,000 | 221 | $3.09 B | $601.5 M | $2.49 B |
| [Benin City](Benin-City/README.md) | 1,800,000 | 162 | $1.74 B | $358.1 M | $1.38 B |
| [Onitsha](Onitsha/README.md) | 1,500,000 | 210 | $9.20 B | $1.52 B | $7.68 B |
| [Maiduguri](Maiduguri/README.md) | 1,200,000 | 191 | $8.19 B | $1.34 B | $6.85 B |
| [Ilorin](Ilorin/README.md) | 1,000,000 | 130 | $717.9 M | $150.4 M | $567.5 M |
| [Aba Ng](Aba-Ng/README.md) | 900,000 | 87 | $517.7 M | $107.3 M | $410.5 M |
| [Jos](Jos/README.md) | 900,000 | 117 | $647.9 M | $131.3 M | $516.6 M |
| [Uyo](Uyo/README.md) | 800,000 | 83 | $476.4 M | $99.1 M | $377.3 M |

## Local Basis And Regeneration

Country finance parameters use `NG` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
