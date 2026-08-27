# Hail — Urban Rail Network

**Country:** SA · **Population:** 500,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Hail-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$743 M (86.4%) of external capital** and **$913 M of external interest**. Capital plus saved interest totals **$1.66 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Hail rail network on OpenStreetMap](hail-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 23 / 1 |
| Route length | 63.1 km double track |
| Coverage / transfer reachability | 46.9% / 33% |
| Estimated station catchment | 234,500 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 133 × 3-car `light-metro-3car` trainsets (120 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 25.3 km | 10 | 53 | S Outer ↔ N Outer |
| line-2 | 21.9 km | 9 | 48 | SW Outer ↔ NE Mid |
| line-3 | 15.9 km | 4 | 32 | N Outer ↔ SE Mid |
| **Total** | **63.1 km** | **23 unique** | **133** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 29,348 train-km/day |
| Annual traction demand | 138.8 GWh |
| Station/depot PV / storage | 11.0 MW / 50.0 MWh |
| Aggregate charging power | 10.5 MW |
| Dedicated solar plant | 60.3 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 7.0 km / 57 kWh |
| Lowest traversal charging margin | line-3: 38 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $177 M |
| Stations | $91 M |
| Depots | $8.0 M |
| Rolling stock | $120 M |
| Dedicated solar plant | $48 M |
| Residual train control | $3.2 M |
| Charging microgrids | $2.3 M |
| EPC / project services | $28 M |
| **Total city programme** | **$478 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $117 M (24.5%) |
| Domestic / local capital | $361 M (75.5%) |
| Annual public construction commitment | $33 M / yr for 5 years |
| Annual post-grace debt service | $23 M / yr |
| External capital saved vs default turnkey sensitivity | $743 M |
| Capital + lifetime external interest saved | $1.66 bn |
| Annual OPEX | $22 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 270 assets / 1,283 tasks | [`hail-operations-manifest.json`](operations/hail-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`hail.toml`](hail.toml) | Expanded simulator scenario |
| [`hail.corridor.geojson`](hail.corridor.geojson) | GIS corridor and stations |
| [`hail.design-quality.yaml`](hail.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
scripts/regenerate-city.sh hail
```
