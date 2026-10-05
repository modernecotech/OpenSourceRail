# Egypt National OpenSourceRail Strategy

This page contains only Egypt-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$20.34 B (88.5%) of external capital** and **$25.01 B of external interest**. Capital plus saved interest totals **$45.35 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 19 |
| Represented population | 10,600,000 |
| Trainsets / vehicle modules | 2,331 / 6,841 |
| City infrastructure and fleet CAPEX | $12.10 B |
| Shared national factory | $624.7 M |
| Factory sizing basis | 636 modules for Tanta, then reused nationally |
| **Total national programme** | **$12.77 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $2.64 B (20.7%) |
| Domestic / local capital | $10.13 B (79.3%) |
| Annual external capital draw | $528.3 M / yr |
| Annual local capital draw | $2.03 B / yr |
| Annual public construction commitment | $1.37 B / yr for 5 years |
| Annual post-grace debt service | $1.03 B / yr |
| Default foreign-turnkey external capital | $22.98 B |
| External capital saved | $20.34 B |
| Capital + lifetime external interest saved | $45.35 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $6.79 B | $1.02 B | $5.77 B |
| Stations | $1.06 B | $212.1 M | $848.4 M |
| Depots | $985.3 M | $246.3 M | $739.0 M |
| Rolling stock | $2.05 B | $716.2 M | $1.33 B |
| Dedicated solar plants | $374.3 M | $168.5 M | $205.9 M |
| Residual train control | $38.2 M | $19.1 M | $19.1 M |
| Charging microgrids | $35.5 M | $14.2 M | $21.3 M |
| EPC / project services | $810.8 M | $121.6 M | $689.2 M |
| Shared national trainset factory | $624.7 M | $124.9 M | $499.8 M |
| **Total** | **$12.77 B** | **$2.64 B** | **$10.13 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Mansoura Eg](Mansoura-Eg/README.md) | 1,000,000 | 132 | $700.8 M | $144.8 M | $556.0 M |
| [Port Said](Port-Said/README.md) | 800,000 | 65 | $379.9 M | $77.2 M | $302.7 M |
| [Suez](Suez/README.md) | 800,000 | 166 | $803.4 M | $170.1 M | $633.3 M |
| [Tanta](Tanta/README.md) | 750,000 | 212 | $1.00 B | $215.0 M | $786.9 M |
| [Ismailia](Ismailia/README.md) | 700,000 | 126 | $664.4 M | $137.9 M | $526.5 M |
| [Zagazig](Zagazig/README.md) | 700,000 | 117 | $611.6 M | $127.7 M | $484.0 M |
| [Asyut](Asyut/README.md) | 600,000 | 149 | $694.5 M | $148.9 M | $545.6 M |
| [Mahalla](Mahalla/README.md) | 600,000 | 107 | $530.3 M | $111.7 M | $418.6 M |
| [Minya](Minya/README.md) | 600,000 | 127 | $669.1 M | $139.0 M | $530.1 M |
| [Sohag](Sohag/README.md) | 550,000 | 110 | $563.2 M | $117.3 M | $445.9 M |
| [Damanhur](Damanhur/README.md) | 500,000 | 130 | $659.1 M | $138.4 M | $520.8 M |
| [Fayoum](Fayoum/README.md) | 500,000 | 186 | $899.7 M | $190.4 M | $709.3 M |
| [Luxor](Luxor/README.md) | 500,000 | 131 | $675.2 M | $140.4 M | $534.8 M |
| [Damietta](Damietta/README.md) | 400,000 | 200 | $928.9 M | $199.4 M | $729.5 M |
| [Beni Suef](Beni-Suef/README.md) | 350,000 | 94 | $530.5 M | $108.0 M | $422.4 M |
| [Qena](Qena/README.md) | 350,000 | 127 | $773.9 M | $154.3 M | $619.6 M |
| [Arish](Arish/README.md) | 300,000 | 26 | $162.7 M | $31.4 M | $131.4 M |
| [Hurghada](Hurghada/README.md) | 300,000 | 69 | $452.8 M | $84.8 M | $368.0 M |
| [Kafr El Sheikh](Kafr-El-Sheikh/README.md) | 300,000 | 57 | $397.1 M | $73.5 M | $323.6 M |

## Local Basis And Regeneration

Country finance parameters use `EG` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
