# Mukalla — Urban Rail Network

**Country:** YE · **Population:** 550,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Mukalla-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$715 M (85.9%) of external capital** and **$924 M of external interest**. Capital plus saved interest totals **$1.64 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Mukalla rail network on OpenStreetMap](mukalla-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 22 / 1 |
| Route length | 61.6 km double track |
| Coverage / transfer reachability | 62.8% / 33% |
| Estimated station catchment | 345,400 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 152 × 3-car `light-metro-3car` trainsets (137 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 19.2 km | 8 | 48 | SW Outer ↔ NE Mid |
| line-2 | 16.5 km | 5 | 40 | E Mid ↔ SW Outer |
| line-3 | 26.0 km | 9 | 64 | NE Outer ↔ SW Outer |
| **Total** | **61.6 km** | **22 unique** | **152** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 28,649 train-km/day |
| Annual traction demand | 135.5 GWh |
| Station/depot PV / storage | 10.1 MW / 48.5 MWh |
| Aggregate charging power | 9.0 MW |
| Dedicated solar plant | 59.5 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 9.9 km / 80 kWh |
| Lowest traversal charging margin | line-2: 50 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $163 M |
| Stations | $75 M |
| Depots | $8.0 M |
| Rolling stock | $137 M |
| Dedicated solar plant | $48 M |
| Residual train control | $3.1 M |
| Charging microgrids | $1.9 M |
| EPC / project services | $27 M |
| **Total city programme** | **$462 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $117 M (25.3%) |
| Domestic / local capital | $345 M (74.7%) |
| Annual public construction commitment | $62 M / yr for 10 years |
| Annual post-grace debt service | $57 M / yr |
| External capital saved vs default turnkey sensitivity | $715 M |
| Capital + lifetime external interest saved | $1.64 bn |
| Annual OPEX | $12 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 284 assets / 1,397 tasks | [`mukalla-operations-manifest.json`](operations/mukalla-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`mukalla.toml`](mukalla.toml) | Expanded simulator scenario |
| [`mukalla.corridor.geojson`](mukalla.corridor.geojson) | GIS corridor and stations |
| [`mukalla.design-quality.yaml`](mukalla.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh mukalla
```
