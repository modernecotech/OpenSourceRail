# Asyut — Urban Rail Network

**Country:** EG · **Population:** 600,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Asyut-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$740 M (86.1%) of external capital** and **$910 M of external interest**. Capital plus saved interest totals **$1.65 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Asyut rail network on OpenStreetMap](asyut-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 19 / 2 |
| Route length | 51.7 km double track |
| Coverage / transfer reachability | 69.8% / 100% |
| Estimated station catchment | 418,800 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 162 × 3-car `light-metro-3car` trainsets (146 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 |  7.6 km | 4 | 26 | S Inner ↔ NW Mid |
| line-2 | 19.7 km | 7 | 62 | W Mid ↔ NE Outer |
| line-3 | 24.4 km | 8 | 74 | SE Outer ↔ W Outer |
| **Total** | **51.7 km** | **19 unique** | **162** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 24,060 train-km/day |
| Annual traction demand | 113.8 GWh |
| Station/depot PV / storage | 9.2 MW / 47.0 MWh |
| Aggregate charging power | 7.5 MW |
| Dedicated solar plant | 49.2 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 12.0 km / 97 kWh |
| Lowest traversal charging margin | line-1: 30 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $161 M |
| Stations | $90 M |
| Depots | $8.0 M |
| Rolling stock | $146 M |
| Dedicated solar plant | $39 M |
| Residual train control | $2.6 M |
| Charging microgrids | $1.8 M |
| EPC / project services | $29 M |
| **Total city programme** | **$477 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $119 M (25.0%) |
| Domestic / local capital | $358 M (75.0%) |
| Annual public construction commitment | $50 M / yr for 5 years |
| Annual post-grace debt service | $38 M / yr |
| External capital saved vs default turnkey sensitivity | $740 M |
| Capital + lifetime external interest saved | $1.65 bn |
| Annual OPEX | $13 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 283 assets / 1,426 tasks | [`asyut-operations-manifest.json`](operations/asyut-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`asyut.toml`](asyut.toml) | Expanded simulator scenario |
| [`asyut.corridor.geojson`](asyut.corridor.geojson) | GIS corridor and stations |
| [`asyut.design-quality.yaml`](asyut.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
scripts/regenerate-city.sh asyut
```
