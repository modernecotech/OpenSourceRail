# Iraq National OpenSourceRail Strategy

<!-- OSR CURRENT SCOPE CONTEXT -->
> **Original catalogue or earlier scope reference.** The figures and policies below retain their original assumptions; they are not the latest Baghdad staffing, depot, procurement or funding basis. See the [current Baghdad recalculation](Baghdad/engineering/programme-recalculation/README.md) and [current city summary](Baghdad/README.md). National/portfolio totals have not been repriced with that conditional Baghdad option.
<!-- END OSR CURRENT SCOPE CONTEXT -->

This page contains only Iraq-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$55.81 B (88.4%) of external capital** and **$68.62 B of external interest**. Capital plus saved interest totals **$124.43 B**.

The [Baghdad physical factory plan](Baghdad/engineering/factory/README.md) sizes production cells and test paths for its current six-car trainset order to finish alongside the overall city infrastructure programme, with facility readiness at 18 months from NTP. The national aggregation uses the largest physical city-order capital envelope across Iraq or the original module allowance, counted once. Any allowance above the Baghdad plant belongs to future national scope. Future city loads are not concurrent factory commitments or part of Baghdad finance.

## Iraq financing

The catalogue-wide figures below are generic capital/benchmark aggregations. They do not establish a five-year rollout or an Iraq lender commitment. The scheduled proposal covers **Baghdad only**, including one manufacturing plant. It uses government capital at **25% of total CAPEX**, imports split 50% government USD cash / 50% proposed Chinese USD credit, with the remaining government capital, bonds and bank credit in IQD. Full-basket Chinese eligibility remains unqualified. Additional cash requirements beyond that public contribution remain visible in the [Baghdad funding programme](IRAQ-FUNDING-PROGRAMME.md). Samawah, Mosul and every other Iraqi city are excluded from its cashflows.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 18 |
| Represented population | 29,491,199 |
| Trainsets / vehicle modules | 3,836 / 16,295 |
| City infrastructure and fleet CAPEX | $34.22 B |
| Shared national factory | $794.6 M |
| Factory sizing basis | 4,632 modules for Baghdad, then reused nationally |
| **Total national programme** | **$35.07 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $7.31 B (20.9%) |
| Domestic / local capital | $27.76 B (79.1%) |
| Default foreign-turnkey external capital | $63.12 B |
| External capital saved | $55.81 B |
| Capital + lifetime external interest saved | $124.43 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $19.25 B | $2.89 B | $16.36 B |
| Stations | $4.42 B | $883.0 M | $3.53 B |
| Depots | $1.36 B | $340.3 M | $1.02 B |
| Rolling stock | $4.65 B | $1.63 B | $3.02 B |
| Dedicated solar plants | $2.11 B | $948.9 M | $1.16 B |
| Residual train control | $103.6 M | $51.8 M | $51.8 M |
| Charging microgrids | $227.8 M | $91.1 M | $136.7 M |
| EPC / project services | $2.16 B | $323.4 M | $1.83 B |
| Shared national trainset factory | $794.6 M | $158.9 M | $635.7 M |
| **Total** | **$35.07 B** | **$7.31 B** | **$27.76 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Baghdad](Baghdad/README.md) | 9,780,429 | 772 | $7.23 B | $1.64 B | $5.59 B |
| [Basra](Basra/README.md) | 3,955,000 | 428 | $5.25 B | $1.11 B | $4.14 B |
| [Sulaymaniyah](Sulaymaniyah/README.md) | 2,150,000 | 121 | $1.67 B | $333.2 M | $1.34 B |
| [Erbil](Erbil/README.md) | 1,952,000 | 216 | $1.81 B | $383.0 M | $1.43 B |
| [Mosul](Mosul/README.md) | 1,940,000 | 256 | $3.26 B | $632.9 M | $2.63 B |
| [Kirkuk](Kirkuk/README.md) | 1,780,000 | 164 | $2.06 B | $400.5 M | $1.66 B |
| [Najaf](Najaf/README.md) | 1,540,000 | 239 | $2.58 B | $523.9 M | $2.05 B |
| [Karbala](Karbala/README.md) | 1,390,000 | 191 | $2.33 B | $461.1 M | $1.87 B |
| [Nasiriyah](Nasiriyah/README.md) | 705,000 | 139 | $869.2 M | $172.9 M | $696.3 M |
| [Hillah](Hillah/README.md) | 700,000 | 168 | $843.9 M | $178.3 M | $665.7 M |
| [Amarah](Amarah/README.md) | 660,000 | 137 | $860.4 M | $171.5 M | $689.0 M |
| [Ramadi](Ramadi/README.md) | 525,000 | 118 | $704.2 M | $143.4 M | $560.8 M |
| [Baqubah](Baqubah/README.md) | 470,000 | 176 | $926.1 M | $192.9 M | $733.3 M |
| [Diwaniyah](Diwaniyah/README.md) | 440,000 | 128 | $683.4 M | $141.1 M | $542.3 M |
| [Kut](Kut/README.md) | 410,000 | 142 | $918.3 M | $182.0 M | $736.3 M |
| [Samawah](Samawah/README.md) | 373,770 | 132 | $710.6 M | $148.0 M | $562.6 M |
| [Duhok](Duhok/README.md) | 360,000 | 163 | $782.8 M | $173.8 M | $608.9 M |
| [Fallujah](Fallujah/README.md) | 360,000 | 146 | $740.6 M | $155.3 M | $585.2 M |

## Local Basis And Regeneration

Country finance parameters use `IQ` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
