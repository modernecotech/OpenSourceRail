# Saudi Arabia National OpenSourceRail Strategy

This page contains only Saudi Arabia-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$39.91 B (88.4%) of external capital** and **$49.07 B of external interest**. Capital plus saved interest totals **$88.98 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 14 |
| Represented population | 15,600,000 |
| Trainsets / vehicle modules | 3,206 / 12,124 |
| City infrastructure and fleet CAPEX | $24.23 B |
| Shared national factory | $804.8 M |
| Factory sizing basis | 3,360 modules for Jeddah, then reused nationally |
| **Total national programme** | **$25.09 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $5.25 B (20.9%) |
| Domestic / local capital | $19.84 B (79.1%) |
| Annual external capital draw | $1.05 B / yr |
| Annual local capital draw | $3.97 B / yr |
| Annual public construction commitment | $1.74 B / yr for 5 years |
| Annual post-grace debt service | $1.21 B / yr |
| Default foreign-turnkey external capital | $45.16 B |
| External capital saved | $39.91 B |
| Capital + lifetime external interest saved | $88.98 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $13.39 B | $2.01 B | $11.38 B |
| Stations | $3.02 B | $603.4 M | $2.41 B |
| Depots | $1.24 B | $309.4 M | $928.3 M |
| Rolling stock | $3.50 B | $1.23 B | $2.28 B |
| Dedicated solar plants | $1.36 B | $612.8 M | $749.0 M |
| Residual train control | $78.4 M | $39.2 M | $39.2 M |
| Charging microgrids | $145.2 M | $58.1 M | $87.1 M |
| EPC / project services | $1.55 B | $232.8 M | $1.32 B |
| Shared national trainset factory | $804.8 M | $161.0 M | $643.8 M |
| **Total** | **$25.09 B** | **$5.25 B** | **$19.84 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Jeddah](Jeddah/README.md) | 4,700,000 | 560 | $5.84 B | $1.29 B | $4.55 B |
| [Mecca](Mecca/README.md) | 2,200,000 | 260 | $2.94 B | $588.5 M | $2.35 B |
| [Dammam](Dammam/README.md) | 1,500,000 | 346 | $3.61 B | $741.6 M | $2.86 B |
| [Medina](Medina/README.md) | 1,500,000 | 220 | $2.66 B | $526.2 M | $2.14 B |
| [Hofuf](Hofuf/README.md) | 800,000 | 226 | $1.02 B | $221.2 M | $795.0 M |
| [Buraidah](Buraidah/README.md) | 700,000 | 184 | $918.0 M | $194.0 M | $723.9 M |
| [Taif](Taif/README.md) | 700,000 | 176 | $896.9 M | $187.9 M | $709.0 M |
| [Tabuk](Tabuk/README.md) | 650,000 | 181 | $929.4 M | $194.6 M | $734.7 M |
| [Khamis Mushait](Khamis-Mushait/README.md) | 600,000 | 224 | $1.07 B | $227.9 M | $838.6 M |
| [Hail](Hail/README.md) | 500,000 | 174 | $865.4 M | $182.9 M | $682.5 M |
| [Najran](Najran/README.md) | 500,000 | 160 | $1.00 B | $199.5 M | $802.0 M |
| [Abha](Abha/README.md) | 450,000 | 157 | $789.5 M | $165.2 M | $624.3 M |
| [Al Kharj](Al-Kharj/README.md) | 400,000 | 187 | $897.7 M | $191.4 M | $706.3 M |
| [Jizan](Jizan/README.md) | 400,000 | 151 | $804.4 M | $169.0 M | $635.4 M |

## Local Basis And Regeneration

Country finance parameters use `SA` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
