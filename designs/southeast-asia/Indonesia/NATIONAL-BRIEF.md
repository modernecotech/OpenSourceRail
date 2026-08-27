# Indonesia National OpenSourceRail Strategy

This page contains only Indonesia-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$9.07 B (86.1%) of external capital** and **$11.15 B of external interest**. Capital plus saved interest totals **$20.22 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 2 |
| Represented population | 5,624,000 |
| Trainsets / vehicle modules | 782 / 4,068 |
| City infrastructure and fleet CAPEX | $5.67 B |
| Shared national factory | $169.2 M |
| Factory sizing basis | 2,820 modules for Surabaya, then reused nationally |
| **Total national programme** | **$5.85 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.46 B (25.0%) |
| Domestic / local capital | $4.39 B (75.0%) |
| Annual external capital draw | $293.0 M / yr |
| Annual local capital draw | $877.6 M / yr |
| Annual public construction commitment | $476.6 M / yr for 5 years |
| Annual post-grace debt service | $346.2 M / yr |
| Default foreign-turnkey external capital | $10.54 B |
| External capital saved | $9.07 B |
| Capital + lifetime external interest saved | $20.22 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $2.04 B | $305.9 M | $1.73 B |
| Stations | $1.19 B | $238.4 M | $953.5 M |
| Depots | $16.0 M | $4.0 M | $12.0 M |
| Rolling stock | $1.14 B | $398.7 M | $740.4 M |
| Dedicated solar plants | $876.7 M | $394.5 M | $482.2 M |
| Residual train control | $27.0 M | $13.5 M | $13.5 M |
| Charging microgrids | $68.3 M | $27.3 M | $41.0 M |
| EPC / project services | $325.6 M | $48.8 M | $276.7 M |
| Shared national trainset factory | $169.2 M | $33.8 M | $135.4 M |
| **Total** | **$5.85 B** | **$1.46 B** | **$4.39 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Surabaya](Surabaya/README.md) | 3,009,000 | 470 | $3.41 B | $893.2 M | $2.52 B |
| [Bandung](Bandung/README.md) | 2,615,000 | 312 | $2.26 B | $536.1 M | $1.72 B |

## Local Basis And Regeneration

Country finance parameters use `ID` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 scripts/generate-national-briefs.py
```
