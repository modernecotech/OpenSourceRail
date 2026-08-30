# Cuenca — Urban Rail Network

**Country:** EC · **Population:** 817,100 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Cuenca-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$851 M (85.7%) of external capital** and **$1.05 bn of external interest**. Capital plus saved interest totals **$1.90 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Cuenca rail network on OpenStreetMap](cuenca-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 24 / 1 |
| Route length | 70.9 km double track |
| Coverage / transfer reachability | 64.3% / 100% |
| Estimated station catchment | 525,395 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 169 × 3-car `light-metro-3car` trainsets (152 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 26.1 km | 9 | 61 | E Mid ↔ W Outer |
| line-2 | 24.1 km | 8 | 58 | NE Outer ↔ W Mid |
| line-3 | 20.7 km | 7 | 50 | NW Mid ↔ SE Outer |
| **Total** | **70.9 km** | **24 unique** | **169** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 32,968 train-km/day |
| Annual traction demand | 156.0 GWh |
| Station/depot PV / storage | 10.7 MW / 49.5 MWh |
| Aggregate charging power | 10.0 MW |
| Dedicated solar plant | 90.1 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 13.6 km / 102 kWh |
| Lowest traversal charging margin | line-2: 71 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $197 M |
| Stations | $85 M |
| Depots | $8.0 M |
| Rolling stock | $152 M |
| Dedicated solar plant | $72 M |
| Residual train control | $3.5 M |
| Charging microgrids | $2.1 M |
| EPC / project services | $31 M |
| **Total city programme** | **$551 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $142 M (25.7%) |
| Domestic / local capital | $410 M (74.3%) |
| Annual public construction commitment | $54 M / yr for 5 years |
| Annual post-grace debt service | $41 M / yr |
| External capital saved vs default turnkey sensitivity | $851 M |
| Capital + lifetime external interest saved | $1.90 bn |
| Annual OPEX | $16 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 314 assets / 1,549 tasks | [`cuenca-operations-manifest.json`](operations/cuenca-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`cuenca.toml`](cuenca.toml) | Expanded simulator scenario |
| [`cuenca.corridor.geojson`](cuenca.corridor.geojson) | GIS corridor and stations |
| [`cuenca.design-quality.yaml`](cuenca.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh cuenca
```
