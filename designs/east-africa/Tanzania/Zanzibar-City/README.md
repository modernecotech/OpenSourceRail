# Zanzibar-City — Urban Rail Network

**Country:** TZ · **Population:** 500,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Zanzibar-City-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$926 M (86.8%) of external capital** and **$1.16 bn of external interest**. Capital plus saved interest totals **$2.09 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Zanzibar-City rail network on OpenStreetMap](zanzibar-city-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 22 / 4 |
| Route length | 61.9 km double track |
| Coverage / transfer reachability | 71.7% / 100% |
| Estimated station catchment | 358,500 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 134 × 3-car `light-metro-3car` trainsets (120 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 19.1 km | 7 | 41 | N Outer ↔ S Mid |
| line-2 | 21.0 km | 7 | 46 | NW Outer ↔ E Mid |
| line-3 | 21.7 km | 8 | 47 | SE Outer ↔ N Mid |
| **Total** | **61.9 km** | **22 unique** | **134** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 28,762 train-km/day |
| Annual traction demand | 136.1 GWh |
| Station/depot PV / storage | 11.0 MW / 50.0 MWh |
| Aggregate charging power | 10.5 MW |
| Dedicated solar plant | 76.7 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 7.0 km / 53 kWh |
| Lowest traversal charging margin | line-1: 71 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $219 M |
| Stations | $144 M |
| Depots | $8.0 M |
| Rolling stock | $121 M |
| Dedicated solar plant | $61 M |
| Residual train control | $3.1 M |
| Charging microgrids | $2.5 M |
| EPC / project services | $35 M |
| **Total city programme** | **$593 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $141 M (23.8%) |
| Domestic / local capital | $452 M (76.2%) |
| Annual public construction commitment | $54 M / yr for 7 years |
| Annual post-grace debt service | $44 M / yr |
| External capital saved vs default turnkey sensitivity | $926 M |
| Capital + lifetime external interest saved | $2.09 bn |
| Annual OPEX | $14 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 271 assets / 1,282 tasks | [`zanzibar-city-operations-manifest.json`](operations/zanzibar-city-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`zanzibar-city.toml`](zanzibar-city.toml) | Expanded simulator scenario |
| [`zanzibar-city.corridor.geojson`](zanzibar-city.corridor.geojson) | GIS corridor and stations |
| [`zanzibar-city.design-quality.yaml`](zanzibar-city.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
scripts/regenerate-city.sh zanzibar-city
```
