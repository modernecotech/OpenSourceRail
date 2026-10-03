# Baghdad — Urban Rail Network

**Country:** IQ · **Population:** 9,780,429 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Baghdad-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$11.87 bn (87.3%) of external capital** and **$14.60 bn of external interest**. Capital plus saved interest totals **$26.47 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Baghdad rail network on OpenStreetMap](baghdad-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 9 / 182 / 23 |
| Route length | 516.5 km double track |
| Coverage / transfer reachability | 46.4% / 44% |
| Estimated station catchment | 4,538,119 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 831 × 6-car `metro-6car` trainsets (751 peak revenue) |
| Peak network throughput | 259,200 passengers/hour |
| Practical service capacity | 2,276,640 passenger-trips/day |
| Annual paid-trip planning range | 415.5–664.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 53.8 km | 19 | 95 | S Outer ↔ N Outer |
| line-2 | 57.0 km | 21 | 103 | SE Outer ↔ NW Mid |
| line-3 | 55.8 km | 21 | 108 | S Outer ↔ NE Outer |
| line-4 | 44.4 km | 16 | 85 | NW Outer ↔ E Mid |
| line-5 | 53.7 km | 18 | 98 | W Mid ↔ E Outer |
| line-6 | 57.5 km | 19 | 111 | SW Outer ↔ NE Mid |
| line-7 | 43.5 km | 16 | 84 | E Outer ↔ SW Mid |
| line-8 | 51.4 km | 18 | 100 | SE Outer ↔ NW Mid |
| line-9 | 99.3 km | 34 | 47 | NW Mid ↔ NW Mid |
| **Total** | **516.5 km** | **182 unique** | **831** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 3,952 one-way journeys / 217,090 train-km/day |
| Annual traction demand | 2,053.8 GWh |
| Station/depot PV / storage | 52.1 MW / 354.0 MWh |
| Aggregate charging power | 316.0 MW |
| Dedicated solar plant | 1,018.6 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-8: 21.3 km / 344 kWh |
| Lowest traversal charging margin | line-5: 304 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $3.89 bn |
| Stations | $908 M |
| Depots | $8.0 M |
| Rolling stock | $1.40 bn |
| Dedicated solar plant | $815 M |
| Residual train control | $26 M |
| Charging microgrids | $68 M |
| EPC / project services | $441 M |
| **Total city programme** | **$7.56 bn** |

## Iraq funding

Proposed facilities and appropriations remain uncommitted. The conditional ledger calculates government capital and the extra support required for fees, interest, reserves and cash shortfalls; additional support is not a funding commitment.

| Capital source | Planning USD equivalent |
|---|---:|
| bank credit | $1.20 bn |
| chinese export credit | $865 M |
| domestic bonds | $3.60 bn |
| government | $1.89 bn |

The procurement schedule requires **347 calendar months** of capital cash under an assumed 260-working-day year. The resource-constrained full-network rollout needs review before a construction commitment.

Peak annual government cash: **$687 M**. This includes support required under the low capacity-use case; it is not a funded appropriation.

Chinese export buyer credit is allocated within existing imported budgets for solar equipment, bogies, batteries, windows and doors. City CAPEX excludes manufacturing tooling; the Baghdad-only programme separately funds one plant for Baghdad. IQD bonds assume a proposed Ministry of Finance programme; municipal borrowing authority is pending legal review.

The model includes actual scheduled draws, native-currency principal/interest, fees, revenue ramps, operating/debt support, reserve movements and downside cases. Short bullet bonds have explicit redemptions without assumed refinancing.

See [funding model](engineering/finance/FUNDING-MODEL.md), [monthly cashflow](engineering/finance/funding-monthly-cashflow.csv), [annual cashflow](engineering/finance/funding-annual-cashflow.csv) and [Baghdad-only funding programme](../IRAQ-FUNDING-PROGRAMME.md). Government capital is 25% of total CAPEX, including USD cash for half the imports; the other half uses proposed Chinese USD credit. The remaining government capital, bonds, bank credit and local cash are IQD. Full import-basket loan eligibility is an unqualified scenario assumption. Additional support is a separate unfunded requirement if public cash is capped at that contribution.

Conditional phased-opening sensitivity: first / last line revenue starts in month **66 / 346** from financial close. City additional support is **$7.90 bn**, excluding the separately financed plant. Fleet-weighted revenue, independent ramps and a 25% fixed OPEX allowance require a validated phase-specific operating plan. Actual plant, depot and line acceptance remain pending.

Annual operating allowance: $181 M; demand remains capacity-led.

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 69 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 1,862 assets / 10,785 tasks | [`baghdad-operations-manifest.json`](operations/baghdad-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`baghdad.toml`](baghdad.toml) | Expanded simulator scenario |
| [`baghdad.corridor.geojson`](baghdad.corridor.geojson) | GIS corridor and stations |
| [`baghdad.design-quality.yaml`](baghdad.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh baghdad
```
