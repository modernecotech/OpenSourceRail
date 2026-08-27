# Mogadishu — Urban Rail Network

**Country:** SO · **Population:** 2,610,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Mogadishu-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$1.67 bn (87.1%) of external capital** and **$2.16 bn of external interest**. Capital plus saved interest totals **$3.82 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Mogadishu rail network on OpenStreetMap](mogadishu-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 4 / 48 / 6 |
| Route length | 120.7 km double track |
| Coverage / transfer reachability | 56.1% / 100% |
| Estimated station catchment | 1,464,210 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 149 × 4-car `metro-4car` trainsets (134 peak revenue) |
| Peak network throughput | 76,800 passengers/hour |
| Practical service capacity | 624,960 passenger-trips/day |
| Annual paid-trip planning range | 114.1–182.5 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 37.1 km | 14 | 58 | E Inner ↔ NW Outer |
| line-2 | 24.9 km | 11 | 43 | E Mid ↔ SW Mid |
| line-3 | 16.7 km | 8 | 31 | NW Inner ↔ SE Inner |
| line-4 | 42.0 km | 15 | 17 | N Mid ↔ N Inner |
| **Total** | **120.7 km** | **48 unique** | **149** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,628 one-way journeys / 46,358 train-km/day |
| Annual traction demand | 292.4 GWh |
| Station/depot PV / storage | 17.9 MW / 104.5 MWh |
| Aggregate charging power | 66.0 MW |
| Dedicated solar plant | 133.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 12.5 km / 135 kWh |
| Lowest traversal charging margin | line-4: 140 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $401 M |
| Stations | $298 M |
| Depots | $8.0 M |
| Rolling stock | $167 M |
| Dedicated solar plant | $106 M |
| Residual train control | $6.0 M |
| Charging microgrids | $15 M |
| EPC / project services | $63 M |
| **Total city programme** | **$1.06 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $246 M (23.2%) |
| Domestic / local capital | $817 M (76.8%) |
| Annual public construction commitment | $126 M / yr for 10 years |
| Annual post-grace debt service | $115 M / yr |
| External capital saved vs default turnkey sensitivity | $1.67 bn |
| Capital + lifetime external interest saved | $3.82 bn |
| Annual OPEX | $24 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 415 assets / 1,767 tasks | [`mogadishu-operations-manifest.json`](operations/mogadishu-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`mogadishu.toml`](mogadishu.toml) | Expanded simulator scenario |
| [`mogadishu.corridor.geojson`](mogadishu.corridor.geojson) | GIS corridor and stations |
| [`mogadishu.design-quality.yaml`](mogadishu.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
scripts/regenerate-city.sh mogadishu
```
