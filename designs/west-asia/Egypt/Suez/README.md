# Suez — Urban Rail Network

**Country:** EG · **Population:** 800,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Suez-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$716 M (86.4%) of external capital** and **$880 M of external interest**. Capital plus saved interest totals **$1.60 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Suez rail network on OpenStreetMap](suez-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 23 / 1 |
| Route length | 60.6 km double track |
| Coverage / transfer reachability | 57.4% / 33% |
| Estimated station catchment | 459,199 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 129 × 3-car `light-metro-3car` trainsets (116 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 24.6 km | 10 | 54 | SE Outer ↔ NW Mid |
| line-2 | 17.7 km | 7 | 37 | SW Mid ↔ NE Mid |
| line-3 | 18.3 km | 6 | 38 | N Mid ↔ W Mid |
| **Total** | **60.6 km** | **23 unique** | **129** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 28,169 train-km/day |
| Annual traction demand | 133.3 GWh |
| Station/depot PV / storage | 10.7 MW / 49.5 MWh |
| Aggregate charging power | 10.0 MW |
| Dedicated solar plant | 57.7 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 11.5 km / 93 kWh |
| Lowest traversal charging margin | line-3: 42 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $170 M |
| Stations | $87 M |
| Depots | $8.0 M |
| Rolling stock | $116 M |
| Dedicated solar plant | $46 M |
| Residual train control | $3.0 M |
| Charging microgrids | $2.2 M |
| EPC / project services | $27 M |
| **Total city programme** | **$460 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $113 M (24.5%) |
| Domestic / local capital | $347 M (75.5%) |
| Annual public construction commitment | $48 M / yr for 5 years |
| Annual post-grace debt service | $37 M / yr |
| External capital saved vs default turnkey sensitivity | $716 M |
| Capital + lifetime external interest saved | $1.60 bn |
| Annual OPEX | $12 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 265 assets / 1,252 tasks | [`suez-operations-manifest.json`](operations/suez-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`suez.toml`](suez.toml) | Expanded simulator scenario |
| [`suez.corridor.geojson`](suez.corridor.geojson) | GIS corridor and stations |
| [`suez.design-quality.yaml`](suez.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
scripts/regenerate-city.sh suez
```
