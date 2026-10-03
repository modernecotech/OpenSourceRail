# Fallujah — Urban Rail Network

**Country:** IQ · **Population:** 360,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Fallujah-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$705 M (86.6%) of external capital** and **$867 M of external interest**. Capital plus saved interest totals **$1.57 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Fallujah rail network on OpenStreetMap](fallujah-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 21 / 1 |
| Route length | 55.8 km double track |
| Coverage / transfer reachability | 70.5% / 100% |
| Estimated station catchment | 253,800 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 122 × 3-car `light-metro-3car` trainsets (109 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 21.0 km | 8 | 46 | NW Outer ↔ SE Mid |
| line-2 | 15.8 km | 6 | 35 | W Mid ↔ E Mid |
| line-3 | 19.0 km | 7 | 41 | SE Outer ↔ W Inner |
| **Total** | **55.8 km** | **21 unique** | **122** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 25,937 train-km/day |
| Annual traction demand | 122.7 GWh |
| Station/depot PV / storage | 11.0 MW / 50.0 MWh |
| Aggregate charging power | 10.5 MW |
| Dedicated solar plant | 51.8 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 6.6 km / 54 kWh |
| Lowest traversal charging margin | line-2: 56 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $164 M |
| Stations | $98 M |
| Depots | $8.0 M |
| Rolling stock | $110 M |
| Dedicated solar plant | $41 M |
| Residual train control | $2.8 M |
| Charging microgrids | $2.3 M |
| EPC / project services | $27 M |
| **Total city programme** | **$452 M** |

## Iraq funding

Proposed facilities and appropriations remain uncommitted. Government funds eligible-invoice downpayments, its capital share, fees, interest, restricted reserves and cash shortfalls.

| Capital source | Planning USD equivalent |
|---|---:|
| bank credit | $41 M |
| chinese export credit | $44 M |
| domestic bonds | $122 M |
| government | $245 M |

The procurement schedule requires **59 calendar months** of capital cash under an assumed 260-working-day year. The resource-constrained full-network rollout needs review before a construction commitment.

Peak annual government cash: **$212 M**. This includes support required under the low capacity-use case; it is not a funded appropriation.

Chinese export buyer credit is allocated within existing imported budgets for solar equipment, bogies, batteries, windows and doors. Shared national manufacturing tooling is funded once at programme level. IQD bonds assume a proposed Ministry of Finance programme; municipal borrowing authority is pending legal review.

The model includes actual scheduled draws, native-currency principal/interest, fees, revenue ramps, operating/debt support, reserve movements and downside cases. Short bullet bonds have explicit redemptions without assumed refinancing.

See [funding model](engineering/finance/FUNDING-MODEL.md), [monthly cashflow](engineering/finance/funding-monthly-cashflow.csv), [annual cashflow](engineering/finance/funding-annual-cashflow.csv) and [three-city funding programme](../IRAQ-FUNDING-PROGRAMME.md).

Annual operating allowance: $13 M; demand remains capacity-led.

## Local Evidence

**Evidence refresh required.** Retained passing results below are unverified.
The strict README generator rejected the evidence: engineering/simulation/validation-summary.json describes scenario SHA-256 42970b88e5c4fc0c8522701289ce2d79b4b72867a3217e13cd20b327355f1666, but fallujah.toml is 7e874f2163c523a8758c047761abcd5a8750440f9d788ef6c1542df9a5db6188; rerun and update the validation evidence. This audit view does not accept or replace the retained solver results.

| Package | Current status | Evidence |
|---|---|---|
| Finance | unverified | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | unverified | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | unverified | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | unverified; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | unverified | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | unverified; 0 findings; 10 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 250 assets / 1,486 tasks | [`fallujah-operations-manifest.json`](operations/fallujah-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`fallujah.toml`](fallujah.toml) | Expanded simulator scenario |
| [`fallujah.corridor.geojson`](fallujah.corridor.geojson) | GIS corridor and stations |
| [`fallujah.design-quality.yaml`](fallujah.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh fallujah
```
