# Morocco National OpenSourceRail Strategy

This page contains only Morocco-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$11.32 B (86.9%) of external capital** and **$13.92 B of external interest**. Capital plus saved interest totals **$25.25 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 12 |
| Represented population | 8,050,000 |
| Trainsets / vehicle modules | 1,421 / 4,643 |
| City infrastructure and fleet CAPEX | $7.17 B |
| Shared national factory | $61.2 M |
| Factory sizing basis | 1,020 modules for Marrakech, then reused nationally |
| **Total national programme** | **$7.24 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.70 B (23.5%) |
| Domestic / local capital | $5.54 B (76.5%) |
| Annual external capital draw | $340.1 M / yr |
| Annual local capital draw | $1.11 B / yr |
| Annual public construction commitment | $497.2 M / yr for 5 years |
| Annual post-grace debt service | $351.0 M / yr |
| Default foreign-turnkey external capital | $13.02 B |
| External capital saved | $11.32 B |
| Capital + lifetime external interest saved | $25.25 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $2.75 B | $413.0 M | $2.34 B |
| Stations | $1.73 B | $345.8 M | $1.38 B |
| Depots | $96.0 M | $24.0 M | $72.0 M |
| Rolling stock | $1.34 B | $469.1 M | $871.3 M |
| Dedicated solar plants | $721.7 M | $324.8 M | $397.0 M |
| Residual train control | $43.0 M | $21.5 M | $21.5 M |
| Charging microgrids | $64.8 M | $25.9 M | $38.9 M |
| EPC / project services | $426.1 M | $63.9 M | $362.2 M |
| Shared national trainset factory | $61.2 M | $12.2 M | $49.0 M |
| **Total** | **$7.24 B** | **$1.70 B** | **$5.54 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Fez](Fez/README.md) | 1,300,000 | 128 | $1.04 B | $236.3 M | $803.5 M |
| [Marrakech](Marrakech/README.md) | 1,200,000 | 255 | $1.55 B | $371.0 M | $1.18 B |
| [Tangier](Tangier/README.md) | 1,200,000 | 181 | $1.26 B | $296.4 M | $961.5 M |
| [Agadir](Agadir/README.md) | 900,000 | 172 | $656.0 M | $158.5 M | $497.5 M |
| [Meknes](Meknes/README.md) | 700,000 | 89 | $343.3 M | $83.0 M | $260.4 M |
| [Oujda](Oujda/README.md) | 600,000 | 81 | $339.4 M | $80.0 M | $259.4 M |
| [Kenitra](Kenitra/README.md) | 500,000 | 130 | $461.7 M | $114.9 M | $346.8 M |
| [Tetouan](Tetouan/README.md) | 500,000 | 115 | $486.3 M | $114.1 M | $372.2 M |
| [Safi](Safi/README.md) | 350,000 | 86 | $347.2 M | $83.3 M | $263.8 M |
| [Beni Mellal](Beni-Mellal/README.md) | 300,000 | 66 | $242.5 M | $53.0 M | $189.5 M |
| [Khouribga](Khouribga/README.md) | 250,000 | 46 | $181.8 M | $38.6 M | $143.2 M |
| [Nador](Nador/README.md) | 250,000 | 72 | $266.7 M | $58.3 M | $208.4 M |

## Local Basis And Regeneration

Country finance parameters use `MA` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
