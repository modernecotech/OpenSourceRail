# Egypt National OpenSourceRail Strategy

This page contains only Egypt-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$21.50 B (88.5%) of external capital** and **$26.43 B of external interest**. Capital plus saved interest totals **$47.94 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 19 |
| Represented population | 10,600,000 |
| Trainsets / vehicle modules | 2,398 / 7,040 |
| City infrastructure and fleet CAPEX | $12.81 B |
| Shared national factory | $640.9 M |
| Factory sizing basis | 654 modules for Tanta, then reused nationally |
| **Total national programme** | **$13.49 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $2.78 B (20.6%) |
| Domestic / local capital | $10.71 B (79.4%) |
| Annual external capital draw | $556.9 M / yr |
| Annual local capital draw | $2.14 B / yr |
| Annual public construction commitment | $1.45 B / yr for 5 years |
| Annual post-grace debt service | $1.09 B / yr |
| Default foreign-turnkey external capital | $24.29 B |
| External capital saved | $21.50 B |
| Capital + lifetime external interest saved | $47.94 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $7.04 B | $1.06 B | $5.98 B |
| Stations | $1.39 B | $278.7 M | $1.11 B |
| Depots | $996.1 M | $249.0 M | $747.1 M |
| Rolling stock | $2.11 B | $737.0 M | $1.37 B |
| Dedicated solar plants | $384.5 M | $173.0 M | $211.5 M |
| Residual train control | $39.0 M | $19.5 M | $19.5 M |
| Charging microgrids | $37.5 M | $15.0 M | $22.5 M |
| EPC / project services | $857.5 M | $128.6 M | $728.9 M |
| Shared national trainset factory | $640.9 M | $128.2 M | $512.7 M |
| **Total** | **$13.49 B** | **$2.78 B** | **$10.71 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Mansoura Eg](Mansoura-Eg/README.md) | 1,000,000 | 141 | $778.7 M | $159.8 M | $618.9 M |
| [Port Said](Port-Said/README.md) | 800,000 | 65 | $403.4 M | $81.1 M | $322.3 M |
| [Suez](Suez/README.md) | 800,000 | 172 | $867.4 M | $182.6 M | $684.8 M |
| [Tanta](Tanta/README.md) | 750,000 | 218 | $1.03 B | $222.0 M | $810.3 M |
| [Ismailia](Ismailia/README.md) | 700,000 | 141 | $798.3 M | $164.3 M | $633.9 M |
| [Zagazig](Zagazig/README.md) | 700,000 | 118 | $615.7 M | $128.5 M | $487.2 M |
| [Asyut](Asyut/README.md) | 600,000 | 148 | $694.1 M | $148.5 M | $545.6 M |
| [Mahalla](Mahalla/README.md) | 600,000 | 107 | $543.7 M | $114.3 M | $429.4 M |
| [Minya](Minya/README.md) | 600,000 | 129 | $691.6 M | $143.3 M | $548.3 M |
| [Sohag](Sohag/README.md) | 550,000 | 110 | $573.0 M | $118.8 M | $454.2 M |
| [Damanhur](Damanhur/README.md) | 500,000 | 132 | $668.3 M | $140.4 M | $527.9 M |
| [Fayoum](Fayoum/README.md) | 500,000 | 190 | $945.2 M | $200.0 M | $745.2 M |
| [Luxor](Luxor/README.md) | 500,000 | 139 | $753.1 M | $155.6 M | $597.6 M |
| [Damietta](Damietta/README.md) | 400,000 | 208 | $1.01 B | $216.7 M | $797.8 M |
| [Beni Suef](Beni-Suef/README.md) | 350,000 | 95 | $558.6 M | $113.4 M | $445.2 M |
| [Qena](Qena/README.md) | 350,000 | 131 | $814.7 M | $162.6 M | $652.1 M |
| [Arish](Arish/README.md) | 300,000 | 26 | $162.7 M | $31.4 M | $131.4 M |
| [Hurghada](Hurghada/README.md) | 300,000 | 72 | $481.7 M | $90.7 M | $391.0 M |
| [Kafr El Sheikh](Kafr-El-Sheikh/README.md) | 300,000 | 56 | $409.3 M | $75.8 M | $333.5 M |

## Local Basis And Regeneration

Country finance parameters use `EG` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
