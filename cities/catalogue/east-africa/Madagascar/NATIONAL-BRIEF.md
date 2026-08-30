# Madagascar National OpenSourceRail Strategy

This page contains only Madagascar-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$5.55 B (85.3%) of external capital** and **$7.16 B of external interest**. Capital plus saved interest totals **$12.71 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 1 |
| Represented population | 3,058,000 |
| Trainsets / vehicle modules | 504 / 3,024 |
| City infrastructure and fleet CAPEX | $3.42 B |
| Shared national factory | $181.4 M |
| Factory sizing basis | 3,024 modules for Antananarivo, then reused nationally |
| **Total national programme** | **$3.61 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $952.9 M (26.4%) |
| Domestic / local capital | $2.66 B (73.6%) |
| Annual external capital draw | $95.3 M / yr |
| Annual local capital draw | $265.8 M / yr |
| Annual public construction commitment | $329.9 M / yr for 10 years |
| Annual post-grace debt service | $303.1 M / yr |
| Default foreign-turnkey external capital | $6.50 B |
| External capital saved | $5.55 B |
| Capital + lifetime external interest saved | $12.71 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $1.17 B | $175.2 M | $992.7 M |
| Stations | $521.8 M | $104.4 M | $417.4 M |
| Depots | $8.0 M | $2.0 M | $6.0 M |
| Rolling stock | $846.7 M | $296.4 M | $550.4 M |
| Dedicated solar plants | $636.4 M | $286.4 M | $350.0 M |
| Residual train control | $16.2 M | $8.1 M | $8.1 M |
| Charging microgrids | $37.7 M | $15.1 M | $22.6 M |
| EPC / project services | $194.6 M | $29.2 M | $165.4 M |
| Shared national trainset factory | $181.4 M | $36.3 M | $145.2 M |
| **Total** | **$3.61 B** | **$952.9 M** | **$2.66 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Antananarivo](Antananarivo/README.md) | 3,058,000 | 504 | $3.42 B | $914.7 M | $2.50 B |

## Local Basis And Regeneration

Country finance parameters use `MG` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
