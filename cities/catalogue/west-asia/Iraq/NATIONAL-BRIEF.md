# Iraq National OpenSourceRail Strategy

<!-- OSR CURRENT SCOPE CONTEXT -->
> **Original catalogue or earlier scope reference.** The figures and policies below retain their original assumptions; they are not the latest Baghdad staffing, depot, procurement or funding basis. See the [current Baghdad recalculation](Baghdad/engineering/programme-recalculation/README.md) and [current city summary](Baghdad/README.md). National/portfolio totals have not been repriced with that conditional Baghdad option.
<!-- END OSR CURRENT SCOPE CONTEXT -->

This page contains only Iraq-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$36.41 B (87.0%) of external capital** and **$44.76 B of external interest**. Capital plus saved interest totals **$81.17 B**.

The [Baghdad physical factory plan](Baghdad/engineering/factory/README.md) sizes production cells and test paths for its current six-car trainset order to finish alongside the overall city infrastructure programme, with facility readiness at 18 months from NTP. The national aggregation uses the larger of that physical capital envelope and the original module allowance, counted once. Future city loads are not concurrent factory commitments or part of Baghdad finance.

## Iraq financing

The catalogue-wide figures below are generic capital/benchmark aggregations. They do not establish a five-year rollout or an Iraq lender commitment. The scheduled proposal covers **Baghdad only**, including one manufacturing plant. It uses government capital at **25% of total CAPEX**, imports split 50% government USD cash / 50% proposed Chinese USD credit, with the remaining government capital, bonds and bank credit in IQD. Full-basket Chinese eligibility remains unqualified. Additional cash requirements beyond that public contribution remain visible in the [Baghdad funding programme](IRAQ-FUNDING-PROGRAMME.md). Samawah, Mosul and every other Iraqi city are excluded from its cashflows.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 18 |
| Represented population | 29,491,199 |
| Trainsets / vehicle modules | 3,581 / 15,582 |
| City infrastructure and fleet CAPEX | $22.91 B |
| Shared national factory | $323.9 M |
| Factory sizing basis | 4,572 modules for Baghdad, then reused nationally |
| **Total national programme** | **$23.26 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $5.45 B (23.5%) |
| Domestic / local capital | $17.80 B (76.5%) |
| Default foreign-turnkey external capital | $41.86 B |
| External capital saved | $36.41 B |
| Capital + lifetime external interest saved | $81.17 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $10.31 B | $1.55 B | $8.76 B |
| Stations | $3.81 B | $762.9 M | $3.05 B |
| Depots | $144.0 M | $36.0 M | $108.0 M |
| Rolling stock | $4.43 B | $1.55 B | $2.88 B |
| Dedicated solar plants | $2.55 B | $1.15 B | $1.40 B |
| Residual train control | $112.3 M | $56.2 M | $56.2 M |
| Charging microgrids | $208.8 M | $83.5 M | $125.3 M |
| EPC / project services | $1.35 B | $203.2 M | $1.15 B |
| Shared national trainset factory | $323.9 M | $64.8 M | $259.1 M |
| **Total** | **$23.26 B** | **$5.45 B** | **$17.80 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Baghdad](Baghdad/README.md) | 9,780,429 | 762 | $7.17 B | $1.62 B | $5.55 B |
| [Basra](Basra/README.md) | 3,955,000 | 450 | $3.11 B | $793.5 M | $2.32 B |
| [Sulaymaniyah](Sulaymaniyah/README.md) | 2,150,000 | 129 | $1.03 B | $243.5 M | $783.0 M |
| [Erbil](Erbil/README.md) | 1,952,000 | 212 | $1.02 B | $262.0 M | $758.5 M |
| [Mosul](Mosul/README.md) | 1,940,000 | 256 | $1.93 B | $431.6 M | $1.50 B |
| [Kirkuk](Kirkuk/README.md) | 1,780,000 | 179 | $1.17 B | $273.5 M | $893.6 M |
| [Najaf](Najaf/README.md) | 1,540,000 | 229 | $1.52 B | $354.4 M | $1.17 B |
| [Karbala](Karbala/README.md) | 1,390,000 | 198 | $1.37 B | $319.5 M | $1.05 B |
| [Nasiriyah](Nasiriyah/README.md) | 705,000 | 147 | $538.7 M | $125.7 M | $413.0 M |
| [Hillah](Hillah/README.md) | 700,000 | 125 | $461.2 M | $111.8 M | $349.4 M |
| [Amarah](Amarah/README.md) | 660,000 | 101 | $433.0 M | $99.4 M | $333.6 M |
| [Ramadi](Ramadi/README.md) | 525,000 | 104 | $430.3 M | $101.4 M | $328.9 M |
| [Baqubah](Baqubah/README.md) | 470,000 | 130 | $479.2 M | $116.4 M | $362.8 M |
| [Diwaniyah](Diwaniyah/README.md) | 440,000 | 106 | $434.5 M | $101.5 M | $333.1 M |
| [Kut](Kut/README.md) | 410,000 | 101 | $426.6 M | $97.9 M | $328.7 M |
| [Samawah](Samawah/README.md) | 373,770 | 108 | $415.3 M | $100.0 M | $315.4 M |
| [Duhok](Duhok/README.md) | 360,000 | 122 | $518.5 M | $127.7 M | $390.8 M |
| [Fallujah](Fallujah/README.md) | 360,000 | 122 | $452.4 M | $109.5 M | $342.9 M |

## Local Basis And Regeneration

Country finance parameters use `IQ` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
