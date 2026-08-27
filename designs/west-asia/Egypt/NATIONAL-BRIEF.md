# Egypt National OpenSourceRail Strategy

This page contains only Egypt-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$11.97 B (86.7%) of external capital** and **$14.71 B of external interest**. Capital plus saved interest totals **$26.68 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 19 |
| Represented population | 10,600,000 |
| Trainsets / vehicle modules | 2,094 / 6,099 |
| City infrastructure and fleet CAPEX | $7.63 B |
| Shared national factory | $34.2 M |
| Factory sizing basis | 570 modules for Fayoum, then reused nationally |
| **Total national programme** | **$7.67 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.84 B (23.9%) |
| Domestic / local capital | $5.83 B (76.1%) |
| Annual external capital draw | $367.3 M / yr |
| Annual local capital draw | $1.17 B / yr |
| Annual public construction commitment | $805.8 M / yr for 5 years |
| Annual post-grace debt service | $610.4 M / yr |
| Default foreign-turnkey external capital | $13.80 B |
| External capital saved | $11.97 B |
| Capital + lifetime external interest saved | $26.68 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $2.76 B | $414.1 M | $2.35 B |
| Stations | $1.71 B | $342.1 M | $1.37 B |
| Depots | $152.0 M | $38.0 M | $114.0 M |
| Rolling stock | $1.82 B | $637.8 M | $1.18 B |
| Dedicated solar plants | $645.1 M | $290.3 M | $354.8 M |
| Residual train control | $45.6 M | $22.8 M | $22.8 M |
| Charging microgrids | $38.4 M | $15.3 M | $23.0 M |
| EPC / project services | $459.5 M | $68.9 M | $390.6 M |
| Shared national trainset factory | $34.2 M | $6.8 M | $27.4 M |
| **Total** | **$7.67 B** | **$1.84 B** | **$5.83 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Mansoura Eg](Mansoura-Eg/README.md) | 1,000,000 | 109 | $421.1 M | $101.3 M | $319.8 M |
| [Port Said](Port-Said/README.md) | 800,000 | 64 | $317.5 M | $71.7 M | $245.7 M |
| [Suez](Suez/README.md) | 800,000 | 129 | $460.2 M | $112.9 M | $347.3 M |
| [Tanta](Tanta/README.md) | 750,000 | 176 | $549.0 M | $139.4 M | $409.5 M |
| [Ismailia](Ismailia/README.md) | 700,000 | 119 | $422.2 M | $102.5 M | $319.8 M |
| [Zagazig](Zagazig/README.md) | 700,000 | 92 | $390.4 M | $91.5 M | $298.9 M |
| [Asyut](Asyut/README.md) | 600,000 | 162 | $477.4 M | $119.2 M | $358.2 M |
| [Mahalla](Mahalla/README.md) | 600,000 | 84 | $334.6 M | $79.2 M | $255.4 M |
| [Minya](Minya/README.md) | 600,000 | 114 | $438.2 M | $104.7 M | $333.5 M |
| [Sohag](Sohag/README.md) | 550,000 | 98 | $394.4 M | $93.0 M | $301.4 M |
| [Damanhur](Damanhur/README.md) | 500,000 | 103 | $382.5 M | $92.7 M | $289.8 M |
| [Fayoum](Fayoum/README.md) | 500,000 | 190 | $533.1 M | $137.1 M | $396.1 M |
| [Luxor](Luxor/README.md) | 500,000 | 111 | $415.7 M | $100.6 M | $315.1 M |
| [Damietta](Damietta/README.md) | 400,000 | 156 | $573.4 M | $139.5 M | $433.9 M |
| [Beni Suef](Beni-Suef/README.md) | 350,000 | 87 | $323.1 M | $78.2 M | $244.9 M |
| [Qena](Qena/README.md) | 350,000 | 117 | $416.9 M | $100.8 M | $316.1 M |
| [Arish](Arish/README.md) | 300,000 | 38 | $166.0 M | $34.6 M | $131.4 M |
| [Hurghada](Hurghada/README.md) | 300,000 | 80 | $347.8 M | $73.4 M | $274.4 M |
| [Kafr El Sheikh](Kafr-El-Sheikh/README.md) | 300,000 | 65 | $268.4 M | $56.8 M | $211.6 M |

## Local Basis And Regeneration

Country finance parameters use `EG` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 scripts/generate-national-briefs.py
```
