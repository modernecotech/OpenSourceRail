# Saudi Arabia National OpenSourceRail Strategy

This page contains only Saudi Arabia-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$69.30 B (89.7%) of external capital** and **$85.20 B of external interest**. Capital plus saved interest totals **$154.49 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 14 |
| Represented population | 15,600,000 |
| Trainsets / vehicle modules | 3,206 / 12,124 |
| City infrastructure and fleet CAPEX | $42.04 B |
| Shared national factory | $804.8 M |
| Factory sizing basis | 3,360 modules for Jeddah, then reused nationally |
| **Total national programme** | **$42.90 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $7.92 B (18.5%) |
| Domestic / local capital | $34.98 B (81.5%) |
| Annual external capital draw | $1.58 B / yr |
| Annual local capital draw | $7.00 B / yr |
| Annual public construction commitment | $3.01 B / yr for 5 years |
| Annual post-grace debt service | $2.06 B / yr |
| Default foreign-turnkey external capital | $77.22 B |
| External capital saved | $69.30 B |
| Capital + lifetime external interest saved | $154.49 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $30.03 B | $4.50 B | $25.53 B |
| Stations | $3.02 B | $603.4 M | $2.41 B |
| Depots | $1.24 B | $309.4 M | $928.3 M |
| Rolling stock | $3.50 B | $1.23 B | $2.28 B |
| Dedicated solar plants | $1.36 B | $612.8 M | $749.0 M |
| Residual train control | $78.4 M | $39.2 M | $39.2 M |
| Charging microgrids | $145.2 M | $58.1 M | $87.1 M |
| EPC / project services | $2.72 B | $407.6 M | $2.31 B |
| Shared national trainset factory | $804.8 M | $161.0 M | $643.8 M |
| **Total** | **$42.90 B** | **$7.92 B** | **$34.98 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Jeddah](Jeddah/README.md) | 4,700,000 | 560 | $16.05 B | $2.82 B | $13.23 B |
| [Mecca](Mecca/README.md) | 2,200,000 | 260 | $2.94 B | $588.9 M | $2.35 B |
| [Dammam](Dammam/README.md) | 1,500,000 | 346 | $10.90 B | $1.84 B | $9.06 B |
| [Medina](Medina/README.md) | 1,500,000 | 220 | $2.87 B | $557.7 M | $2.31 B |
| [Hofuf](Hofuf/README.md) | 800,000 | 226 | $1.02 B | $221.2 M | $795.0 M |
| [Buraidah](Buraidah/README.md) | 700,000 | 184 | $918.0 M | $194.0 M | $723.9 M |
| [Taif](Taif/README.md) | 700,000 | 176 | $896.9 M | $187.9 M | $709.0 M |
| [Tabuk](Tabuk/README.md) | 650,000 | 181 | $929.4 M | $194.6 M | $734.7 M |
| [Khamis Mushait](Khamis-Mushait/README.md) | 600,000 | 224 | $1.07 B | $228.0 M | $839.4 M |
| [Hail](Hail/README.md) | 500,000 | 174 | $865.4 M | $182.9 M | $682.5 M |
| [Najran](Najran/README.md) | 500,000 | 160 | $1.00 B | $199.5 M | $802.1 M |
| [Abha](Abha/README.md) | 450,000 | 157 | $789.5 M | $165.2 M | $624.3 M |
| [Al Kharj](Al-Kharj/README.md) | 400,000 | 187 | $898.7 M | $191.6 M | $707.2 M |
| [Jizan](Jizan/README.md) | 400,000 | 151 | $894.5 M | $182.5 M | $712.0 M |

## Local Basis And Regeneration

Country finance parameters use `SA` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
