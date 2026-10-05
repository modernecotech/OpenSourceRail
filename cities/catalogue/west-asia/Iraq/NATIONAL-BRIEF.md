# Iraq National OpenSourceRail Strategy

<!-- OSR CURRENT SCOPE CONTEXT -->
> **Original catalogue or earlier scope reference.** The figures and policies below retain their original assumptions; they are not the latest Baghdad staffing, depot, procurement or funding basis. See the [current Baghdad recalculation](Baghdad/engineering/programme-recalculation/README.md) and [current city summary](Baghdad/README.md). National/portfolio totals have not been repriced with that conditional Baghdad option.
<!-- END OSR CURRENT SCOPE CONTEXT -->

This page contains only Iraq-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$54.49 B (88.6%) of external capital** and **$66.99 B of external interest**. Capital plus saved interest totals **$121.49 B**.

The [Baghdad physical factory plan](Baghdad/engineering/factory/README.md) sizes production cells and test paths for its current six-car trainset order to finish alongside the overall city infrastructure programme, with facility readiness at 18 months from NTP. The national aggregation uses the largest physical city-order capital envelope across Iraq or the original module allowance, counted once. Any allowance above the Baghdad plant belongs to future national scope. Future city loads are not concurrent factory commitments or part of Baghdad finance.

## Iraq financing

The catalogue-wide figures below are generic capital/benchmark aggregations. They do not establish a five-year rollout or an Iraq lender commitment. The scheduled proposal covers **Baghdad only**, including one manufacturing plant. It uses government capital at **25% of total CAPEX**, imports split 50% government USD cash / 50% proposed Chinese USD credit, with the remaining government capital, bonds and bank credit in IQD. Full-basket Chinese eligibility remains unqualified. Additional cash requirements beyond that public contribution remain visible in the [Baghdad funding programme](IRAQ-FUNDING-PROGRAMME.md). Samawah, Mosul and every other Iraqi city are excluded from its cashflows.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 18 |
| Represented population | 29,491,199 |
| Trainsets / vehicle modules | 3,652 / 15,530 |
| City infrastructure and fleet CAPEX | $33.36 B |
| Shared national factory | $769.6 M |
| Factory sizing basis | 4,572 modules for Baghdad, then reused nationally |
| **Total national programme** | **$34.19 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $7.05 B (20.6%) |
| Domestic / local capital | $27.14 B (79.4%) |
| Default foreign-turnkey external capital | $61.54 B |
| External capital saved | $54.49 B |
| Capital + lifetime external interest saved | $121.49 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $20.16 B | $3.02 B | $17.14 B |
| Stations | $3.02 B | $603.6 M | $2.41 B |
| Depots | $1.33 B | $332.1 M | $996.3 M |
| Rolling stock | $4.43 B | $1.55 B | $2.88 B |
| Dedicated solar plants | $2.09 B | $941.1 M | $1.15 B |
| Residual train control | $101.2 M | $50.6 M | $50.6 M |
| Charging microgrids | $184.8 M | $73.9 M | $110.9 M |
| EPC / project services | $2.10 B | $315.0 M | $1.78 B |
| Shared national trainset factory | $769.6 M | $153.9 M | $615.7 M |
| **Total** | **$34.19 B** | **$7.05 B** | **$27.14 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Baghdad](Baghdad/README.md) | 9,780,429 | 762 | $7.17 B | $1.62 B | $5.55 B |
| [Basra](Basra/README.md) | 3,955,000 | 396 | $4.73 B | $1.00 B | $3.73 B |
| [Sulaymaniyah](Sulaymaniyah/README.md) | 2,150,000 | 121 | $1.63 B | $325.7 M | $1.31 B |
| [Erbil](Erbil/README.md) | 1,952,000 | 198 | $1.66 B | $350.0 M | $1.31 B |
| [Mosul](Mosul/README.md) | 1,940,000 | 246 | $3.11 B | $602.7 M | $2.50 B |
| [Kirkuk](Kirkuk/README.md) | 1,780,000 | 151 | $1.97 B | $380.7 M | $1.59 B |
| [Najaf](Najaf/README.md) | 1,540,000 | 196 | $2.17 B | $433.3 M | $1.74 B |
| [Karbala](Karbala/README.md) | 1,390,000 | 188 | $3.31 B | $602.1 M | $2.71 B |
| [Nasiriyah](Nasiriyah/README.md) | 705,000 | 136 | $830.4 M | $165.1 M | $665.3 M |
| [Hillah](Hillah/README.md) | 700,000 | 161 | $809.3 M | $170.7 M | $638.6 M |
| [Amarah](Amarah/README.md) | 660,000 | 130 | $817.3 M | $162.1 M | $655.2 M |
| [Ramadi](Ramadi/README.md) | 525,000 | 118 | $683.4 M | $139.2 M | $544.2 M |
| [Baqubah](Baqubah/README.md) | 470,000 | 164 | $850.7 M | $176.5 M | $674.2 M |
| [Diwaniyah](Diwaniyah/README.md) | 440,000 | 120 | $653.2 M | $134.1 M | $519.1 M |
| [Kut](Kut/README.md) | 410,000 | 131 | $793.0 M | $158.1 M | $634.9 M |
| [Samawah](Samawah/README.md) | 373,770 | 133 | $690.6 M | $144.5 M | $546.1 M |
| [Duhok](Duhok/README.md) | 360,000 | 162 | $789.0 M | $174.0 M | $615.1 M |
| [Fallujah](Fallujah/README.md) | 360,000 | 139 | $697.3 M | $146.0 M | $551.3 M |

## Local Basis And Regeneration

Country finance parameters use `IQ` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```
