# Myanmar National OpenSourceRail Strategy

This page contains only Myanmar-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$20.68 B (88.0%) of external capital** and **$26.72 B of external interest**. Capital plus saved interest totals **$47.40 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 2 |
| Represented population | 6,926,000 |
| Trainsets / vehicle modules | 1,089 / 5,968 |
| City infrastructure and fleet CAPEX | $12.12 B |
| Shared national factory | $871.2 M |
| Factory sizing basis | 4,836 modules for Yangon, then reused nationally |
| **Total national programme** | **$13.05 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $2.81 B (21.6%) |
| Domestic / local capital | $10.24 B (78.4%) |
| Annual external capital draw | $281.3 M / yr |
| Annual local capital draw | $1.02 B / yr |
| Annual public construction commitment | $1.40 B / yr for 10 years |
| Annual post-grace debt service | $1.27 B / yr |
| Default foreign-turnkey external capital | $23.49 B |
| External capital saved | $20.68 B |
| Capital + lifetime external interest saved | $47.40 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $6.24 B | $935.5 M | $5.30 B |
| Stations | $1.91 B | $381.4 M | $1.53 B |
| Depots | $437.9 M | $109.5 M | $328.4 M |
| Rolling stock | $1.67 B | $584.9 M | $1.09 B |
| Dedicated solar plants | $1.00 B | $450.7 M | $550.8 M |
| Residual train control | $34.0 M | $17.0 M | $17.0 M |
| Charging microgrids | $105.1 M | $42.0 M | $63.1 M |
| EPC / project services | $788.4 M | $118.3 M | $670.1 M |
| Shared national trainset factory | $871.2 M | $174.2 M | $696.9 M |
| **Total** | **$13.05 B** | **$2.81 B** | **$10.24 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Yangon](Yangon/README.md) | 5,200,000 | 806 | $8.67 B | $1.96 B | $6.72 B |
| [Mandalay](Mandalay/README.md) | 1,726,000 | 283 | $3.45 B | $673.1 M | $2.78 B |

## Local Basis And Regeneration

Country finance parameters use `MM` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
