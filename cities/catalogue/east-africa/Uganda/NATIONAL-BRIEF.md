# Uganda National OpenSourceRail Strategy

This page contains only Uganda-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$17.53 B (89.5%) of external capital** and **$21.98 B of external interest**. Capital plus saved interest totals **$39.52 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 12 |
| Represented population | 4,925,000 |
| Trainsets / vehicle modules | 1,081 / 2,955 |
| City infrastructure and fleet CAPEX | $10.10 B |
| Shared national factory | $735.7 M |
| Factory sizing basis | 940 modules for Kampala, then reused nationally |
| **Total national programme** | **$10.89 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $2.06 B (18.9%) |
| Domestic / local capital | $8.83 B (81.1%) |
| Annual external capital draw | $294.3 M / yr |
| Annual local capital draw | $1.26 B / yr |
| Annual public construction commitment | $1.33 B / yr for 7 years |
| Annual post-grace debt service | $1.12 B / yr |
| Default foreign-turnkey external capital | $19.59 B |
| External capital saved | $17.53 B |
| Capital + lifetime external interest saved | $39.52 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $6.78 B | $1.02 B | $5.77 B |
| Stations | $833.7 M | $166.7 M | $667.0 M |
| Depots | $597.9 M | $149.5 M | $448.4 M |
| Rolling stock | $846.8 M | $296.4 M | $550.4 M |
| Dedicated solar plants | $341.2 M | $153.6 M | $187.7 M |
| Residual train control | $26.7 M | $13.3 M | $13.3 M |
| Charging microgrids | $31.6 M | $12.6 M | $18.9 M |
| EPC / project services | $689.8 M | $103.5 M | $586.4 M |
| Shared national trainset factory | $735.7 M | $147.1 M | $588.6 M |
| **Total** | **$10.89 B** | **$2.06 B** | **$8.83 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Kampala](Kampala/README.md) | 1,875,000 | 235 | $4.94 B | $886.0 M | $4.06 B |
| [Mbarara](Mbarara/README.md) | 500,000 | 150 | $817.7 M | $171.5 M | $646.2 M |
| [Gulu](Gulu/README.md) | 350,000 | 173 | $853.1 M | $184.4 M | $668.7 M |
| [Jinja](Jinja/README.md) | 300,000 | 73 | $473.6 M | $90.7 M | $382.9 M |
| [Mbale](Mbale/README.md) | 300,000 | 47 | $378.5 M | $69.2 M | $309.3 M |
| [Arua](Arua/README.md) | 250,000 | 69 | $471.5 M | $89.7 M | $381.8 M |
| [Entebbe](Entebbe/README.md) | 250,000 | 65 | $402.9 M | $77.4 M | $325.5 M |
| [Lira](Lira/README.md) | 250,000 | 81 | $494.0 M | $95.7 M | $398.4 M |
| [Masaka](Masaka/README.md) | 250,000 | 59 | $400.1 M | $75.3 M | $324.7 M |
| [Fort Portal](Fort-Portal/README.md) | 200,000 | 61 | $421.5 M | $79.8 M | $341.6 M |
| [Hoima](Hoima/README.md) | 200,000 | 51 | $333.4 M | $63.5 M | $270.0 M |
| [Soroti](Soroti/README.md) | 200,000 | 17 | $110.0 M | $22.1 M | $87.9 M |

## Local Basis And Regeneration

Country finance parameters use `UG` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
