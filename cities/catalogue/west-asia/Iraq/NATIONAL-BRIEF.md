# Iraq National OpenSourceRail Strategy

<!-- OSR CURRENT SCOPE CONTEXT -->
> **Original catalogue or earlier scope reference.** The figures and policies below retain their original assumptions; they are not the latest Baghdad staffing, depot, procurement or funding basis. See the [current Baghdad recalculation](Baghdad/engineering/programme-recalculation/README.md) and [current city summary](Baghdad/README.md). National/portfolio totals have not been repriced with that conditional Baghdad option.
<!-- END OSR CURRENT SCOPE CONTEXT -->

This page contains only Iraq-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$93.05 B (89.7%) of external capital** and **$114.40 B of external interest**. Capital plus saved interest totals **$207.45 B**.

The [Baghdad physical factory plan](Baghdad/engineering/factory/README.md) sizes production cells and test paths for its current six-car trainset order to finish alongside the overall city infrastructure programme, with facility readiness at 18 months from NTP. The national aggregation uses the largest physical city-order capital envelope across Iraq or the original module allowance, counted once. Any allowance above the Baghdad plant belongs to future national scope. Future city loads are not concurrent factory commitments or part of Baghdad finance.

## Iraq financing

The catalogue-wide figures below are generic capital/benchmark aggregations. They do not establish a five-year rollout or an Iraq lender commitment. The scheduled proposal covers **Baghdad only**, including one manufacturing plant. It uses government capital at **25% of total CAPEX**, imports split 50% government USD cash / 50% proposed Chinese USD credit, with the remaining government capital, bonds and bank credit in IQD. Full-basket Chinese eligibility remains unqualified. Additional cash requirements beyond that public contribution remain visible in the [Baghdad funding programme](IRAQ-FUNDING-PROGRAMME.md). Samawah, Mosul and every other Iraqi city are excluded from its cashflows.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 18 |
| Represented population | 29,491,199 |
| Trainsets / vehicle modules | 3,836 / 16,295 |
| City infrastructure and fleet CAPEX | $56.79 B |
| Shared national factory | $794.6 M |
| Factory sizing basis | 4,632 modules for Baghdad, then reused nationally |
| **Total national programme** | **$57.64 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $10.70 B (18.6%) |
| Domestic / local capital | $46.94 B (81.4%) |
| Default foreign-turnkey external capital | $103.74 B |
| External capital saved | $93.05 B |
| Capital + lifetime external interest saved | $207.45 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $40.34 B | $6.05 B | $34.29 B |
| Stations | $4.42 B | $883.0 M | $3.53 B |
| Depots | $1.36 B | $340.3 M | $1.02 B |
| Rolling stock | $4.65 B | $1.63 B | $3.02 B |
| Dedicated solar plants | $2.11 B | $948.9 M | $1.16 B |
| Residual train control | $103.6 M | $51.8 M | $51.8 M |
| Charging microgrids | $227.8 M | $91.1 M | $136.7 M |
| EPC / project services | $3.63 B | $544.9 M | $3.09 B |
| Shared national trainset factory | $794.6 M | $158.9 M | $635.7 M |
| **Total** | **$57.64 B** | **$10.70 B** | **$46.94 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Baghdad](Baghdad/README.md) | 9,780,429 | 772 | $14.18 B | $2.69 B | $11.49 B |
| [Basra](Basra/README.md) | 3,955,000 | 428 | $11.90 B | $2.10 B | $9.80 B |
| [Sulaymaniyah](Sulaymaniyah/README.md) | 2,150,000 | 121 | $1.67 B | $333.8 M | $1.34 B |
| [Erbil](Erbil/README.md) | 1,952,000 | 216 | $1.81 B | $383.0 M | $1.43 B |
| [Mosul](Mosul/README.md) | 1,940,000 | 256 | $3.31 B | $640.6 M | $2.67 B |
| [Kirkuk](Kirkuk/README.md) | 1,780,000 | 164 | $2.06 B | $400.5 M | $1.66 B |
| [Najaf](Najaf/README.md) | 1,540,000 | 239 | $7.93 B | $1.33 B | $6.61 B |
| [Karbala](Karbala/README.md) | 1,390,000 | 191 | $3.37 B | $617.1 M | $2.75 B |
| [Nasiriyah](Nasiriyah/README.md) | 705,000 | 139 | $869.2 M | $172.9 M | $696.3 M |
| [Hillah](Hillah/README.md) | 700,000 | 168 | $847.0 M | $178.7 M | $668.2 M |
| [Amarah](Amarah/README.md) | 660,000 | 137 | $860.4 M | $171.5 M | $689.0 M |
| [Ramadi](Ramadi/README.md) | 525,000 | 118 | $721.2 M | $145.9 M | $575.3 M |
| [Baqubah](Baqubah/README.md) | 470,000 | 176 | $926.1 M | $192.9 M | $733.3 M |
| [Diwaniyah](Diwaniyah/README.md) | 440,000 | 128 | $683.4 M | $141.1 M | $542.3 M |
| [Kut](Kut/README.md) | 410,000 | 142 | $3.41 B | $556.4 M | $2.86 B |
| [Samawah](Samawah/README.md) | 373,770 | 132 | $710.6 M | $148.0 M | $562.6 M |
| [Duhok](Duhok/README.md) | 360,000 | 163 | $784.4 M | $174.1 M | $610.3 M |
| [Fallujah](Fallujah/README.md) | 360,000 | 146 | $740.7 M | $155.3 M | $585.3 M |

## Local Basis And Regeneration

Country finance parameters use `IQ` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
