# Indonesia National OpenSourceRail Strategy

This page contains only Indonesia-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$13.11 B (88.1%) of external capital** and **$16.12 B of external interest**. Capital plus saved interest totals **$29.23 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 2 |
| Represented population | 5,624,000 |
| Trainsets / vehicle modules | 658 / 3,414 |
| City infrastructure and fleet CAPEX | $7.37 B |
| Shared national factory | $843.0 M |
| Factory sizing basis | 2,346 modules for Surabaya, then reused nationally |
| **Total national programme** | **$8.27 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.77 B (21.4%) |
| Domestic / local capital | $6.50 B (78.6%) |
| Annual external capital draw | $354.4 M / yr |
| Annual local capital draw | $1.30 B / yr |
| Annual public construction commitment | $687.8 M / yr for 5 years |
| Annual post-grace debt service | $489.8 M / yr |
| Default foreign-turnkey external capital | $14.88 B |
| External capital saved | $13.11 B |
| Capital + lifetime external interest saved | $29.23 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $4.09 B | $613.4 M | $3.48 B |
| Stations | $795.9 M | $159.2 M | $636.7 M |
| Depots | $330.3 M | $82.6 M | $247.7 M |
| Rolling stock | $955.9 M | $334.6 M | $621.3 M |
| Dedicated solar plants | $681.8 M | $306.8 M | $375.0 M |
| Residual train control | $22.9 M | $11.5 M | $11.5 M |
| Charging microgrids | $52.2 M | $20.9 M | $31.3 M |
| EPC / project services | $496.3 M | $74.4 M | $421.8 M |
| Shared national trainset factory | $843.0 M | $168.6 M | $674.4 M |
| **Total** | **$8.27 B** | **$1.77 B** | **$6.50 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Surabaya](Surabaya/README.md) | 3,009,000 | 391 | $4.30 B | $966.5 M | $3.33 B |
| [Bandung](Bandung/README.md) | 2,615,000 | 267 | $3.06 B | $628.0 M | $2.44 B |

## Local Basis And Regeneration

Country finance parameters use `ID` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
