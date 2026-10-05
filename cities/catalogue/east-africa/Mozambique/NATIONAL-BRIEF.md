# Mozambique National OpenSourceRail Strategy

This page contains only Mozambique-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$11.95 B (88.6%) of external capital** and **$15.44 B of external interest**. Capital plus saved interest totals **$27.40 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 10 |
| Represented population | 5,015,000 |
| Trainsets / vehicle modules | 946 / 2,858 |
| City infrastructure and fleet CAPEX | $6.72 B |
| Shared national factory | $721.7 M |
| Factory sizing basis | 928 modules for Maputo, then reused nationally |
| **Total national programme** | **$7.49 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.53 B (20.4%) |
| Domestic / local capital | $5.96 B (79.6%) |
| Annual external capital draw | $153.1 M / yr |
| Annual local capital draw | $596.1 M / yr |
| Annual public construction commitment | $831.9 M / yr for 10 years |
| Annual post-grace debt service | $752.5 M / yr |
| Default foreign-turnkey external capital | $13.49 B |
| External capital saved | $11.95 B |
| Capital + lifetime external interest saved | $27.40 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $3.50 B | $525.0 M | $2.98 B |
| Stations | $1.15 B | $230.3 M | $921.3 M |
| Depots | $481.3 M | $120.3 M | $361.0 M |
| Rolling stock | $830.4 M | $290.6 M | $539.7 M |
| Dedicated solar plants | $276.6 M | $124.5 M | $152.2 M |
| Residual train control | $20.6 M | $10.3 M | $10.3 M |
| Charging microgrids | $37.7 M | $15.1 M | $22.6 M |
| EPC / project services | $472.0 M | $70.8 M | $401.2 M |
| Shared national trainset factory | $721.7 M | $144.3 M | $577.3 M |
| **Total** | **$7.49 B** | **$1.53 B** | **$5.96 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Maputo](Maputo/README.md) | 1,530,000 | 232 | $2.49 B | $520.0 M | $1.97 B |
| [Nampula](Nampula/README.md) | 800,000 | 133 | $718.8 M | $151.6 M | $567.2 M |
| [Beira](Beira/README.md) | 535,000 | 127 | $635.4 M | $137.1 M | $498.3 M |
| [Chimoio](Chimoio/README.md) | 400,000 | 92 | $483.5 M | $103.1 M | $380.4 M |
| [Quelimane](Quelimane/README.md) | 350,000 | 18 | $112.6 M | $23.1 M | $89.5 M |
| [Tete](Tete/README.md) | 350,000 | 132 | $909.9 M | $179.0 M | $730.8 M |
| [Nacala](Nacala/README.md) | 300,000 | 91 | $536.7 M | $106.4 M | $430.3 M |
| [Lichinga](Lichinga/README.md) | 250,000 | 21 | $142.9 M | $27.7 M | $115.2 M |
| [Pemba Mz](Pemba-Mz/README.md) | 250,000 | 55 | $375.3 M | $71.1 M | $304.2 M |
| [Xai Xai](Xai-Xai/README.md) | 250,000 | 45 | $315.1 M | $60.2 M | $254.9 M |

## Local Basis And Regeneration

Country finance parameters use `MZ` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
