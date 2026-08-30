# Surabaya — Urban Rail Network

**Country:** ID · **Population:** 3,009,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Surabaya-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$5.25 bn (85.5%) of external capital** and **$6.46 bn of external interest**. Capital plus saved interest totals **$11.71 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Surabaya rail network on OpenStreetMap](surabaya-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 9 / 102 / 19 |
| Route length | 293.8 km double track |
| Coverage / transfer reachability | 74.2% / 50% |
| Estimated station catchment | 2,232,678 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 470 × 6-car `metro-6car` trainsets (423 peak revenue) |
| Peak network throughput | 259,200 passengers/hour |
| Practical service capacity | 2,276,640 passenger-trips/day |
| Annual paid-trip planning range | 415.5–664.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 35.1 km | 13 | 63 | N Outer ↔ SE Mid |
| line-2 | 33.4 km | 11 | 65 | NE Outer ↔ S Mid |
| line-3 | 37.4 km | 12 | 69 | NE Mid ↔ SW Outer |
| line-4 | 26.3 km | 8 | 49 | N Mid ↔ S Outer |
| line-5 | 33.8 km | 10 | 62 | E Mid ↔ NW Outer |
| line-6 | 24.0 km | 10 | 47 | SW Mid ↔ E Mid |
| line-7 | 23.1 km | 7 | 45 | NW Outer ↔ E Mid |
| line-8 | 21.0 km | 7 | 41 | E Inner ↔ W Mid |
| line-9 | 59.7 km | 24 | 29 | W Mid ↔ W Mid |
| **Total** | **293.8 km** | **102 unique** | **470** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 3,952 one-way journeys / 122,747 train-km/day |
| Annual traction demand | 1,161.3 GWh |
| Station/depot PV / storage | 32.9 MW / 226.0 MWh |
| Aggregate charging power | 188.0 MW |
| Dedicated solar plant | 724.4 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-5: 14.0 km / 210 kWh |
| Lowest traversal charging margin | line-7: 208 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.14 bn |
| Stations | $658 M |
| Depots | $8.0 M |
| Rolling stock | $790 M |
| Dedicated solar plant | $580 M |
| Residual train control | $15 M |
| Charging microgrids | $42 M |
| EPC / project services | $185 M |
| **Total city programme** | **$3.41 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $893 M (26.2%) |
| Domestic / local capital | $2.52 bn (73.8%) |
| Annual public construction commitment | $276 M / yr for 5 years |
| Annual post-grace debt service | $202 M / yr |
| External capital saved vs default turnkey sensitivity | $5.25 bn |
| Capital + lifetime external interest saved | $11.71 bn |
| Annual OPEX | $85 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 1,062 assets / 4,857 tasks | [`surabaya-operations-manifest.json`](operations/surabaya-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`surabaya.toml`](surabaya.toml) | Expanded simulator scenario |
| [`surabaya.corridor.geojson`](surabaya.corridor.geojson) | GIS corridor and stations |
| [`surabaya.design-quality.yaml`](surabaya.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh surabaya
```
