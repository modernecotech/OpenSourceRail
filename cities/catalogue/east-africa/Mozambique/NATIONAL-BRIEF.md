# Mozambique National OpenSourceRail Strategy

This page contains only Mozambique-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$10.79 B (88.7%) of external capital** and **$13.94 B of external interest**. Capital plus saved interest totals **$24.73 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 10 |
| Represented population | 5,015,000 |
| Trainsets / vehicle modules | 853 / 2,588 |
| City infrastructure and fleet CAPEX | $6.06 B |
| Shared national factory | $647.9 M |
| Factory sizing basis | 812 modules for Maputo, then reused nationally |
| **Total national programme** | **$6.76 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.37 B (20.3%) |
| Domestic / local capital | $5.39 B (79.7%) |
| Annual external capital draw | $137.1 M / yr |
| Annual local capital draw | $538.5 M / yr |
| Annual public construction commitment | $751.0 M / yr for 10 years |
| Annual post-grace debt service | $679.1 M / yr |
| Default foreign-turnkey external capital | $12.16 B |
| External capital saved | $10.79 B |
| Capital + lifetime external interest saved | $24.73 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $3.48 B | $521.4 M | $2.95 B |
| Stations | $672.5 M | $134.5 M | $538.0 M |
| Depots | $465.2 M | $116.3 M | $348.9 M |
| Rolling stock | $753.2 M | $263.6 M | $489.6 M |
| Dedicated solar plants | $268.9 M | $121.0 M | $147.9 M |
| Residual train control | $19.4 M | $9.7 M | $9.7 M |
| Charging microgrids | $28.7 M | $11.5 M | $17.2 M |
| EPC / project services | $424.4 M | $63.7 M | $360.8 M |
| Shared national trainset factory | $647.9 M | $129.6 M | $518.3 M |
| **Total** | **$6.76 B** | **$1.37 B** | **$5.39 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Maputo](Maputo/README.md) | 1,530,000 | 203 | $2.32 B | $474.5 M | $1.84 B |
| [Nampula](Nampula/README.md) | 800,000 | 132 | $688.0 M | $145.5 M | $542.5 M |
| [Beira](Beira/README.md) | 535,000 | 127 | $601.5 M | $131.1 M | $470.4 M |
| [Chimoio](Chimoio/README.md) | 400,000 | 94 | $465.9 M | $100.0 M | $366.0 M |
| [Quelimane](Quelimane/README.md) | 350,000 | 18 | $112.6 M | $23.1 M | $89.5 M |
| [Tete](Tete/README.md) | 350,000 | 105 | $655.1 M | $128.9 M | $526.2 M |
| [Nacala](Nacala/README.md) | 300,000 | 62 | $432.4 M | $82.6 M | $349.8 M |
| [Lichinga](Lichinga/README.md) | 250,000 | 21 | $142.9 M | $27.7 M | $115.2 M |
| [Pemba Mz](Pemba-Mz/README.md) | 250,000 | 53 | $369.7 M | $69.9 M | $299.8 M |
| [Xai Xai](Xai-Xai/README.md) | 250,000 | 38 | $275.4 M | $51.7 M | $223.7 M |

## Local Basis And Regeneration

Country finance parameters use `MZ` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
