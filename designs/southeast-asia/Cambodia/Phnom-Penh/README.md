# Phnom-Penh — Urban Rail Network

**Country:** KH · **Population:** 2,281,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Phnom-Penh-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$3.63 bn (87.2%) of external capital** and **$4.55 bn of external interest**. Capital plus saved interest totals **$8.19 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Phnom-Penh rail network on OpenStreetMap](phnom-penh-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 6 / 80 / 14 |
| Route length | 238.4 km double track |
| Coverage / transfer reachability | 75.1% / 80% |
| Estimated station catchment | 1,713,031 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 293 × 4-car `metro-4car` trainsets (264 peak revenue) |
| Peak network throughput | 115,200 passengers/hour |
| Practical service capacity | 982,080 passenger-trips/day |
| Annual paid-trip planning range | 179.2–286.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 30.3 km | 10 | 49 | S Mid ↔ N Outer |
| line-2 | 29.1 km | 11 | 46 | W Mid ↔ SE Outer |
| line-3 | 41.5 km | 14 | 65 | SW Mid ↔ NE Outer |
| line-4 | 33.2 km | 13 | 53 | N Outer ↔ S Mid |
| line-5 | 33.5 km | 13 | 52 | NW Outer ↔ SE Mid |
| line-6 | 70.8 km | 19 | 28 | NW Mid ↔ W Mid |
| **Total** | **238.4 km** | **80 unique** | **293** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,558 one-way journeys / 94,401 train-km/day |
| Annual traction demand | 595.4 GWh |
| Station/depot PV / storage | 24.8 MW / 139.0 MWh |
| Aggregate charging power | 100.5 MW |
| Dedicated solar plant | 362.3 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 18.0 km / 180 kWh |
| Lowest traversal charging margin | line-2: 220 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.06 bn |
| Stations | $459 M |
| Depots | $8.0 M |
| Rolling stock | $328 M |
| Dedicated solar plant | $290 M |
| Residual train control | $12 M |
| Charging microgrids | $22 M |
| EPC / project services | $132 M |
| **Total city programme** | **$2.31 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $533 M (23.0%) |
| Domestic / local capital | $1.78 bn (77.0%) |
| Annual public construction commitment | $189 M / yr for 7 years |
| Annual post-grace debt service | $155 M / yr |
| External capital saved vs default turnkey sensitivity | $3.63 bn |
| Capital + lifetime external interest saved | $8.19 bn |
| Annual OPEX | $53 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 735 assets / 3,247 tasks | [`phnom-penh-operations-manifest.json`](operations/phnom-penh-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`phnom-penh.toml`](phnom-penh.toml) | Expanded simulator scenario |
| [`phnom-penh.corridor.geojson`](phnom-penh.corridor.geojson) | GIS corridor and stations |
| [`phnom-penh.design-quality.yaml`](phnom-penh.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
scripts/regenerate-city.sh phnom-penh
```
