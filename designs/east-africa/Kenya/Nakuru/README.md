# Nakuru — Urban Rail Network

**Country:** KE · **Population:** 700,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Nakuru-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$660 M (86.6%) of external capital** and **$827 M of external interest**. Capital plus saved interest totals **$1.49 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Nakuru rail network on OpenStreetMap](nakuru-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 19 / 1 |
| Route length | 54.3 km double track |
| Coverage / transfer reachability | 46.8% / 100% |
| Estimated station catchment | 327,600 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 116 × 3-car `light-metro-3car` trainsets (104 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 14.8 km | 5 | 30 | NW Mid ↔ E Mid |
| line-2 | 21.3 km | 8 | 47 | NE Mid ↔ SW Outer |
| line-3 | 18.1 km | 6 | 39 | E Outer ↔ W Mid |
| **Total** | **54.3 km** | **19 unique** | **116** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 25,232 train-km/day |
| Annual traction demand | 119.4 GWh |
| Station/depot PV / storage | 10.1 MW / 48.5 MWh |
| Aggregate charging power | 9.0 MW |
| Dedicated solar plant | 46.2 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 8.8 km / 74 kWh |
| Lowest traversal charging margin | line-1: 28 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $154 M |
| Stations | $91 M |
| Depots | $8.0 M |
| Rolling stock | $104 M |
| Dedicated solar plant | $37 M |
| Residual train control | $2.7 M |
| Charging microgrids | $2.0 M |
| EPC / project services | $25 M |
| **Total city programme** | **$424 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $102 M (24.2%) |
| Domestic / local capital | $321 M (75.8%) |
| Annual public construction commitment | $43 M / yr for 7 years |
| Annual post-grace debt service | $36 M / yr |
| External capital saved vs default turnkey sensitivity | $660 M |
| Capital + lifetime external interest saved | $1.49 bn |
| Annual OPEX | $11 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 232 assets / 1,105 tasks | [`nakuru-operations-manifest.json`](operations/nakuru-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`nakuru.toml`](nakuru.toml) | Expanded simulator scenario |
| [`nakuru.corridor.geojson`](nakuru.corridor.geojson) | GIS corridor and stations |
| [`nakuru.design-quality.yaml`](nakuru.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
scripts/regenerate-city.sh nakuru
```
