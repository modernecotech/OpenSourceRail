# Mozambique National OpenSourceRail Strategy

This page contains only Mozambique-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$6.23 B (86.9%) of external capital** and **$8.04 B of external interest**. Capital plus saved interest totals **$14.27 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 10 |
| Represented population | 5,015,000 |
| Trainsets / vehicle modules | 849 / 2,530 |
| City infrastructure and fleet CAPEX | $3.93 B |
| Shared national factory | $51.4 M |
| Factory sizing basis | 856 modules for Maputo, then reused nationally |
| **Total national programme** | **$3.98 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $940.0 M (23.6%) |
| Domestic / local capital | $3.04 B (76.4%) |
| Annual external capital draw | $94.0 M / yr |
| Annual local capital draw | $304.2 M / yr |
| Annual public construction commitment | $431.6 M / yr for 10 years |
| Annual post-grace debt service | $393.7 M / yr |
| Default foreign-turnkey external capital | $7.17 B |
| External capital saved | $6.23 B |
| Capital + lifetime external interest saved | $14.27 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $1.50 B | $225.4 M | $1.28 B |
| Stations | $913.0 M | $182.6 M | $730.4 M |
| Depots | $80.0 M | $20.0 M | $60.0 M |
| Rolling stock | $732.6 M | $256.4 M | $476.2 M |
| Dedicated solar plants | $411.8 M | $185.3 M | $226.5 M |
| Residual train control | $23.1 M | $11.5 M | $11.5 M |
| Charging microgrids | $33.5 M | $13.4 M | $20.1 M |
| EPC / project services | $233.5 M | $35.0 M | $198.5 M |
| Shared national trainset factory | $51.4 M | $10.3 M | $41.1 M |
| **Total** | **$3.98 B** | **$940.0 M** | **$3.04 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Maputo](Maputo/README.md) | 1,530,000 | 214 | $1.48 B | $357.9 M | $1.13 B |
| [Nampula](Nampula/README.md) | 800,000 | 122 | $421.6 M | $106.4 M | $315.2 M |
| [Beira](Beira/README.md) | 535,000 | 96 | $373.7 M | $92.2 M | $281.5 M |
| [Chimoio](Chimoio/README.md) | 400,000 | 82 | $291.5 M | $72.6 M | $218.9 M |
| [Quelimane](Quelimane/README.md) | 350,000 | 23 | $89.8 M | $21.6 M | $68.1 M |
| [Tete](Tete/README.md) | 350,000 | 81 | $377.0 M | $83.0 M | $294.0 M |
| [Nacala](Nacala/README.md) | 300,000 | 81 | $300.6 M | $66.9 M | $233.7 M |
| [Lichinga](Lichinga/README.md) | 250,000 | 34 | $151.3 M | $32.1 M | $119.3 M |
| [Pemba Mz](Pemba-Mz/README.md) | 250,000 | 69 | $272.3 M | $59.4 M | $212.9 M |
| [Xai Xai](Xai-Xai/README.md) | 250,000 | 47 | $165.7 M | $37.1 M | $128.6 M |

## Local Basis And Regeneration

Country finance parameters use `MZ` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
