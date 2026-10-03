# Basra — Urban Rail Network

**Country:** IQ · **Population:** 3,955,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Basra-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$4.81 bn (85.8%) of external capital** and **$5.92 bn of external interest**. Capital plus saved interest totals **$10.73 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Basra rail network on OpenStreetMap](basra-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 7 / 92 / 12 |
| Route length | 305.4 km double track |
| Coverage / transfer reachability | 82.3% / 38% |
| Estimated station catchment | 3,254,965 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 450 × 6-car `metro-6car` trainsets (407 peak revenue) |
| Peak network throughput | 201,600 passengers/hour |
| Practical service capacity | 1,740,960 passenger-trips/day |
| Annual paid-trip planning range | 317.7–508.4 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 45.2 km | 13 | 83 | S Inner ↔ N Outer |
| line-2 | 20.2 km | 8 | 39 | SE Inner ↔ N Mid |
| line-3 | 46.1 km | 13 | 87 | E Outer ↔ NW Mid |
| line-4 | 37.3 km | 12 | 72 | NW Mid ↔ E Outer |
| line-5 | 39.9 km | 13 | 76 | SW Outer ↔ NE Inner |
| line-6 | 29.8 km | 9 | 54 | NW Inner ↔ SW Mid |
| line-7 | 86.9 km | 24 | 39 | N Mid ↔ N Mid |
| **Total** | **305.4 km** | **92 unique** | **450** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 3,022 one-way journeys / 121,804 train-km/day |
| Annual traction demand | 1,152.4 GWh |
| Station/depot PV / storage | 28.1 MW / 194.0 MWh |
| Aggregate charging power | 156.0 MW |
| Dedicated solar plant | 572.8 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 15.2 km / 244 kWh |
| Lowest traversal charging margin | line-2: 229 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.21 bn |
| Stations | $458 M |
| Depots | $8.0 M |
| Rolling stock | $756 M |
| Dedicated solar plant | $458 M |
| Residual train control | $15 M |
| Charging microgrids | $34 M |
| EPC / project services | $174 M |
| **Total city programme** | **$3.11 bn** |

## Iraq funding

Proposed facilities and appropriations remain uncommitted. The conditional ledger calculates government capital and the extra support required for fees, interest, reserves and cash shortfalls; additional support is not a funding commitment.

| Capital source | Planning USD equivalent |
|---|---:|
| bank credit | $274 M |
| chinese export credit | $375 M |
| domestic bonds | $822 M |
| government | $1.64 bn |

The procurement schedule requires **179 calendar months** of capital cash under an assumed 260-working-day year. The resource-constrained full-network rollout needs review before a construction commitment.

Peak annual government cash: **$455 M**. This includes support required under the low capacity-use case; it is not a funded appropriation.

Chinese export buyer credit is allocated within existing imported budgets for solar equipment, bogies, batteries, windows and doors. City CAPEX excludes manufacturing tooling; the Baghdad-only programme separately funds one plant for Baghdad. IQD bonds assume a proposed Ministry of Finance programme; municipal borrowing authority is pending legal review.

The model includes actual scheduled draws, native-currency principal/interest, fees, revenue ramps, operating/debt support, reserve movements and downside cases. Short bullet bonds have explicit redemptions without assumed refinancing.

See [funding model](engineering/finance/FUNDING-MODEL.md), [monthly cashflow](engineering/finance/funding-monthly-cashflow.csv), [annual cashflow](engineering/finance/funding-annual-cashflow.csv) . This standalone city appraisal is outside the Baghdad-only funding programme.

Annual operating allowance: $80 M; demand remains capacity-led.

## Local Evidence

**Evidence refresh required.** Retained passing results below are unverified.
The strict README generator rejected the evidence: engineering/simulation/validation-summary.json describes scenario SHA-256 15a2ae11c07f897271586bba8c882a51b2909cac9f7f8842b41a02f0de940849, but basra.toml is b7ac16966d24ffffc12937860ebbd2b18a9b0ac0dd304d1e2713285b623eddb2; rerun and update the validation evidence. This audit view does not accept or replace the retained solver results.

| Package | Current status | Evidence |
|---|---|---|
| Finance | unverified | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | unverified | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | unverified | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | unverified; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | unverified | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | unverified; 0 findings; 41 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 977 assets / 5,713 tasks | [`basra-operations-manifest.json`](operations/basra-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`basra.toml`](basra.toml) | Expanded simulator scenario |
| [`basra.corridor.geojson`](basra.corridor.geojson) | GIS corridor and stations |
| [`basra.design-quality.yaml`](basra.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh basra
```
