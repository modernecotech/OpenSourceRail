# Eldoret — Urban Rail Network

**Country:** KE · **Population:** 500,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Eldoret-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$746 M (86.1%) of external capital** and **$936 M of external interest**. Capital plus saved interest totals **$1.68 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Eldoret rail network on OpenStreetMap](eldoret-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 20 / 1 |
| Route length | 59.0 km double track |
| Coverage / transfer reachability | 78.7% / 100% |
| Estimated station catchment | 393,500 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 163 × 3-car `light-metro-3car` trainsets (147 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 22.6 km | 7 | 63 | SE Mid ↔ NW Outer |
| line-2 | 14.3 km | 5 | 39 | E Mid ↔ SW Mid |
| line-3 | 22.1 km | 8 | 61 | NW Outer ↔ SE Mid |
| **Total** | **59.0 km** | **20 unique** | **163** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 27,427 train-km/day |
| Annual traction demand | 129.7 GWh |
| Station/depot PV / storage | 9.8 MW / 48.0 MWh |
| Aggregate charging power | 8.5 MW |
| Dedicated solar plant | 51.6 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 11.2 km / 94 kWh |
| Lowest traversal charging margin | line-2: 32 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $167 M |
| Stations | $85 M |
| Depots | $8.0 M |
| Rolling stock | $147 M |
| Dedicated solar plant | $41 M |
| Residual train control | $2.9 M |
| Charging microgrids | $1.9 M |
| EPC / project services | $29 M |
| **Total city programme** | **$482 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $121 M (25.0%) |
| Domestic / local capital | $361 M (75.0%) |
| Annual public construction commitment | $49 M / yr for 7 years |
| Annual post-grace debt service | $41 M / yr |
| External capital saved vs default turnkey sensitivity | $746 M |
| Capital + lifetime external interest saved | $1.68 bn |
| Annual OPEX | $13 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 289 assets / 1,450 tasks | [`eldoret-operations-manifest.json`](operations/eldoret-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`eldoret.toml`](eldoret.toml) | Expanded simulator scenario |
| [`eldoret.corridor.geojson`](eldoret.corridor.geojson) | GIS corridor and stations |
| [`eldoret.design-quality.yaml`](eldoret.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
scripts/regenerate-city.sh eldoret
```
