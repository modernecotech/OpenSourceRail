# Lusaka — Urban Rail Network

**Country:** ZM · **Population:** 3,037,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Lusaka-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$4.35 bn (85.0%) of external capital** and **$5.45 bn of external interest**. Capital plus saved interest totals **$9.80 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Lusaka rail network on OpenStreetMap](lusaka-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 8 / 95 / 13 |
| Route length | 279.5 km double track |
| Coverage / transfer reachability | 58.4% / 36% |
| Estimated station catchment | 1,773,608 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 418 × 6-car `metro-6car` trainsets (376 peak revenue) |
| Peak network throughput | 230,400 passengers/hour |
| Practical service capacity | 2,008,800 passenger-trips/day |
| Annual paid-trip planning range | 366.6–586.6 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 38.5 km | 14 | 74 | NE Outer ↔ W Mid |
| line-2 | 26.2 km | 9 | 47 | E Mid ↔ SW Mid |
| line-3 | 27.5 km | 11 | 52 | SE Outer ↔ W Mid |
| line-4 | 23.8 km | 9 | 45 | E Mid ↔ NW Mid |
| line-5 | 28.4 km | 10 | 51 | N Inner ↔ S Outer |
| line-6 | 32.4 km | 10 | 61 | NE Outer ↔ W Mid |
| line-7 | 28.7 km | 8 | 53 | N Mid ↔ SW Outer |
| line-8 | 73.9 km | 24 | 35 | N Outer ↔ N Mid |
| **Total** | **279.5 km** | **95 unique** | **418** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 3,488 one-way journeys / 112,792 train-km/day |
| Annual traction demand | 1,067.1 GWh |
| Station/depot PV / storage | 30.8 MW / 212.0 MWh |
| Aggregate charging power | 174.0 MW |
| Dedicated solar plant | 665.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-6: 11.0 km / 165 kWh |
| Lowest traversal charging margin | line-7: 214 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $899 M |
| Stations | $498 M |
| Depots | $8.0 M |
| Rolling stock | $702 M |
| Dedicated solar plant | $532 M |
| Residual train control | $14 M |
| Charging microgrids | $38 M |
| EPC / project services | $151 M |
| **Total city programme** | **$2.84 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $767 M (27.0%) |
| Domestic / local capital | $2.08 bn (73.0%) |
| Annual public construction commitment | $368 M / yr for 7 years |
| Annual post-grace debt service | $321 M / yr |
| External capital saved vs default turnkey sensitivity | $4.35 bn |
| Capital + lifetime external interest saved | $9.80 bn |
| Annual OPEX | $69 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 962 assets / 4,378 tasks | [`lusaka-operations-manifest.json`](operations/lusaka-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`lusaka.toml`](lusaka.toml) | Expanded simulator scenario |
| [`lusaka.corridor.geojson`](lusaka.corridor.geojson) | GIS corridor and stations |
| [`lusaka.design-quality.yaml`](lusaka.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
scripts/regenerate-city.sh lusaka
```
