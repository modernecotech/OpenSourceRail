# Saudi Arabia National OpenSourceRail Strategy

This page contains only Saudi Arabia-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$22.67 B (86.4%) of external capital** and **$27.88 B of external interest**. Capital plus saved interest totals **$50.55 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 14 |
| Represented population | 15,600,000 |
| Trainsets / vehicle modules | 2,809 / 11,011 |
| City infrastructure and fleet CAPEX | $14.35 B |
| Shared national factory | $213.1 M |
| Factory sizing basis | 3,552 modules for Jeddah, then reused nationally |
| **Total national programme** | **$14.57 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $3.56 B (24.4%) |
| Domestic / local capital | $11.01 B (75.6%) |
| Annual external capital draw | $712.4 M / yr |
| Annual local capital draw | $2.20 B / yr |
| Annual public construction commitment | $997.3 M / yr for 5 years |
| Annual post-grace debt service | $708.6 M / yr |
| Default foreign-turnkey external capital | $26.23 B |
| External capital saved | $22.67 B |
| Capital + lifetime external interest saved | $50.55 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $5.40 B | $810.2 M | $4.59 B |
| Stations | $2.91 B | $582.5 M | $2.33 B |
| Depots | $112.0 M | $28.0 M | $84.0 M |
| Rolling stock | $3.17 B | $1.11 B | $2.06 B |
| Dedicated solar plants | $1.70 B | $763.1 M | $932.7 M |
| Residual train control | $84.8 M | $42.4 M | $42.4 M |
| Charging microgrids | $145.2 M | $58.1 M | $87.1 M |
| EPC / project services | $842.5 M | $126.4 M | $716.2 M |
| Shared national trainset factory | $213.1 M | $42.6 M | $170.5 M |
| **Total** | **$14.57 B** | **$3.56 B** | **$11.01 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Jeddah](Jeddah/README.md) | 4,700,000 | 592 | $3.76 B | $992.4 M | $2.77 B |
| [Mecca](Mecca/README.md) | 2,200,000 | 271 | $1.81 B | $426.0 M | $1.39 B |
| [Dammam](Dammam/README.md) | 1,500,000 | 325 | $2.20 B | $517.5 M | $1.68 B |
| [Medina](Medina/README.md) | 1,500,000 | 212 | $1.50 B | $347.4 M | $1.15 B |
| [Hofuf](Hofuf/README.md) | 800,000 | 163 | $562.1 M | $139.8 M | $422.3 M |
| [Buraidah](Buraidah/README.md) | 700,000 | 146 | $542.0 M | $131.9 M | $410.1 M |
| [Taif](Taif/README.md) | 700,000 | 125 | $464.4 M | $112.5 M | $351.9 M |
| [Tabuk](Tabuk/README.md) | 650,000 | 134 | $527.7 M | $125.3 M | $402.4 M |
| [Khamis Mushait](Khamis-Mushait/README.md) | 600,000 | 217 | $635.9 M | $161.2 M | $474.7 M |
| [Hail](Hail/README.md) | 500,000 | 133 | $477.8 M | $117.1 M | $360.7 M |
| [Najran](Najran/README.md) | 500,000 | 120 | $521.6 M | $119.2 M | $402.4 M |
| [Abha](Abha/README.md) | 450,000 | 126 | $423.8 M | $105.0 M | $318.8 M |
| [Al Kharj](Al-Kharj/README.md) | 400,000 | 143 | $524.6 M | $128.0 M | $396.6 M |
| [Jizan](Jizan/README.md) | 400,000 | 102 | $388.6 M | $93.8 M | $294.8 M |

## Local Basis And Regeneration

Country finance parameters use `SA` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
