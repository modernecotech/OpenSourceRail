# Duhok — Urban Rail Network

**Country:** IQ · **Population:** 360,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Duhok-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$806 M (86.3%) of external capital** and **$990 M of external interest**. Capital plus saved interest totals **$1.80 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Duhok rail network on OpenStreetMap](duhok-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 22 / 3 |
| Route length | 57.3 km double track |
| Coverage / transfer reachability | 59.9% / 100% |
| Estimated station catchment | 215,640 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 122 × 3-car `light-metro-3car` trainsets (110 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 18.5 km | 8 | 40 | E Outer ↔ W Outer |
| line-2 | 18.3 km | 7 | 40 | W Outer ↔ E Outer |
| line-3 | 20.4 km | 7 | 42 | W Outer ↔ E Outer |
| **Total** | **57.3 km** | **22 unique** | **122** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 26,637 train-km/day |
| Annual traction demand | 126.0 GWh |
| Station/depot PV / storage | 11.3 MW / 50.5 MWh |
| Aggregate charging power | 11.0 MW |
| Dedicated solar plant | 81.5 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 4.9 km / 35 kWh |
| Lowest traversal charging margin | line-3: 67 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $181 M |
| Stations | $119 M |
| Depots | $8.0 M |
| Rolling stock | $110 M |
| Dedicated solar plant | $65 M |
| Residual train control | $2.9 M |
| Charging microgrids | $2.5 M |
| EPC / project services | $30 M |
| **Total city programme** | **$518 M** |

## Iraq funding

Proposed facilities and appropriations remain uncommitted. Government funds eligible-invoice downpayments, its capital share, fees, interest, restricted reserves and cash shortfalls.

| Capital source | Planning USD equivalent |
|---|---:|
| bank credit | $47 M |
| chinese export credit | $53 M |
| domestic bonds | $140 M |
| government | $279 M |

The procurement schedule requires **59 calendar months** of capital cash under an assumed 260-working-day year. The resource-constrained full-network rollout needs review before a construction commitment.

Peak annual government cash: **$248 M**. This includes support required under the low capacity-use case; it is not a funded appropriation.

Chinese export buyer credit is allocated within existing imported budgets for solar equipment, bogies, batteries, windows and doors. Shared national manufacturing tooling is funded once at programme level. IQD bonds assume a proposed Ministry of Finance programme; municipal borrowing authority is pending legal review.

The model includes actual scheduled draws, native-currency principal/interest, fees, revenue ramps, operating/debt support, reserve movements and downside cases. Short bullet bonds have explicit redemptions without assumed refinancing.

See [funding model](engineering/finance/FUNDING-MODEL.md), [monthly cashflow](engineering/finance/funding-monthly-cashflow.csv), [annual cashflow](engineering/finance/funding-annual-cashflow.csv) and [three-city funding programme](../IRAQ-FUNDING-PROGRAMME.md).

Annual operating allowance: $14 M; demand remains capacity-led.

## Local Evidence

**Evidence refresh required.** Retained passing results below are unverified.
The strict README generator rejected the evidence: engineering/simulation/validation-summary.json describes scenario SHA-256 2e62f3d1e5c2b483359d418d24d564ee91f41d7236d465977c9a394751bfa5f0, but duhok.toml is e1bc0fec10f1ba923ae1751109a15e7854c7ba34f0310f9a4474da4149cbdd3f; rerun and update the validation evidence. This audit view does not accept or replace the retained solver results.

| Package | Current status | Evidence |
|---|---|---|
| Finance | unverified | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | unverified | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | unverified | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | unverified; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | unverified | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | unverified; 0 findings; 9 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 257 assets / 1,508 tasks | [`duhok-operations-manifest.json`](operations/duhok-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`duhok.toml`](duhok.toml) | Expanded simulator scenario |
| [`duhok.corridor.geojson`](duhok.corridor.geojson) | GIS corridor and stations |
| [`duhok.design-quality.yaml`](duhok.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh duhok
```
