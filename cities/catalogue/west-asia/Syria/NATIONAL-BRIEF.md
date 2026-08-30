# Syria National OpenSourceRail Strategy

This page contains only Syria-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$8.99 B (86.9%) of external capital** and **$11.61 B of external interest**. Capital plus saved interest totals **$20.59 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 9 |
| Represented population | 7,617,000 |
| Trainsets / vehicle modules | 1,124 / 3,700 |
| City infrastructure and fleet CAPEX | $5.68 B |
| Shared national factory | $56.6 M |
| Factory sizing basis | 944 modules for Damascus, then reused nationally |
| **Total national programme** | **$5.74 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.35 B (23.5%) |
| Domestic / local capital | $4.39 B (76.5%) |
| Annual external capital draw | $134.9 M / yr |
| Annual local capital draw | $439.2 M / yr |
| Annual public construction commitment | $851.3 M / yr for 10 years |
| Annual post-grace debt service | $788.6 M / yr |
| Default foreign-turnkey external capital | $10.33 B |
| External capital saved | $8.99 B |
| Capital + lifetime external interest saved | $20.59 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $2.19 B | $329.1 M | $1.86 B |
| Stations | $1.35 B | $270.7 M | $1.08 B |
| Depots | $72.0 M | $18.0 M | $54.0 M |
| Rolling stock | $1.07 B | $374.0 M | $694.5 M |
| Dedicated solar plants | $572.5 M | $257.6 M | $314.9 M |
| Residual train control | $33.8 M | $16.9 M | $16.9 M |
| Charging microgrids | $52.5 M | $21.0 M | $31.5 M |
| EPC / project services | $338.2 M | $50.7 M | $287.4 M |
| Shared national trainset factory | $56.6 M | $11.3 M | $45.3 M |
| **Total** | **$5.74 B** | **$1.35 B** | **$4.39 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Damascus](Damascus/README.md) | 2,503,000 | 236 | $1.64 B | $383.0 M | $1.26 B |
| [Aleppo](Aleppo/README.md) | 1,639,000 | 219 | $1.57 B | $369.3 M | $1.20 B |
| [Homs](Homs/README.md) | 775,000 | 87 | $357.6 M | $85.1 M | $272.5 M |
| [Latakia](Latakia/README.md) | 700,000 | 93 | $344.7 M | $84.8 M | $259.9 M |
| [Hama](Hama/README.md) | 600,000 | 114 | $406.4 M | $99.2 M | $307.2 M |
| [Deir Ez Zor](Deir-Ez-Zor/README.md) | 500,000 | 143 | $486.2 M | $116.6 M | $369.6 M |
| [Raqqa](Raqqa/README.md) | 350,000 | 105 | $398.0 M | $95.7 M | $302.3 M |
| [Idlib](Idlib/README.md) | 300,000 | 67 | $243.1 M | $53.4 M | $189.7 M |
| [Tartus](Tartus/README.md) | 250,000 | 60 | $232.5 M | $50.3 M | $182.3 M |

## Local Basis And Regeneration

Country finance parameters use `SY` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
