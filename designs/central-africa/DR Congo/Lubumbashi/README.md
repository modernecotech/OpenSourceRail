# Lubumbashi — Urban Rail Network

**Country:** CD · **Population:** 2,829,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Lubumbashi-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$1.58 bn (86.3%) of external capital** and **$2.04 bn of external interest**. Capital plus saved interest totals **$3.61 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Lubumbashi rail network on OpenStreetMap](lubumbashi-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 5 / 41 / 5 |
| Route length | 130.0 km double track |
| Coverage / transfer reachability | 50.8% / 60% |
| Estimated station catchment | 1,437,132 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 161 × 4-car `metro-4car` trainsets (144 peak revenue) |
| Peak network throughput | 96,000 passengers/hour |
| Practical service capacity | 803,520 passenger-trips/day |
| Annual paid-trip planning range | 146.6–234.6 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 22.3 km | 7 | 35 | NE Outer ↔ S Mid |
| line-2 | 21.8 km | 10 | 40 | W Mid ↔ E Mid |
| line-3 | 14.6 km | 4 | 24 | NE Mid ↔ W Mid |
| line-4 | 26.2 km | 9 | 43 | SE Mid ↔ N Outer |
| line-5 | 45.2 km | 11 | 19 | W Mid ↔ W Mid |
| **Total** | **130.0 km** | **41 unique** | **161** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,092 one-way journeys / 49,945 train-km/day |
| Annual traction demand | 315.0 GWh |
| Station/depot PV / storage | 15.8 MW / 94.0 MWh |
| Aggregate charging power | 55.5 MW |
| Dedicated solar plant | 188.6 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-4: 10.6 km / 106 kWh |
| Lowest traversal charging margin | line-3: 109 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $405 M |
| Stations | $195 M |
| Depots | $8.0 M |
| Rolling stock | $180 M |
| Dedicated solar plant | $151 M |
| Residual train control | $6.5 M |
| Charging microgrids | $12 M |
| EPC / project services | $56 M |
| **Total city programme** | **$1.01 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $249 M (24.6%) |
| Domestic / local capital | $765 M (75.4%) |
| Annual public construction commitment | $106 M / yr for 10 years |
| Annual post-grace debt service | $97 M / yr |
| External capital saved vs default turnkey sensitivity | $1.58 bn |
| Capital + lifetime external interest saved | $3.61 bn |
| Annual OPEX | $23 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 393 assets / 1,744 tasks | [`lubumbashi-operations-manifest.json`](operations/lubumbashi-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`lubumbashi.toml`](lubumbashi.toml) | Expanded simulator scenario |
| [`lubumbashi.corridor.geojson`](lubumbashi.corridor.geojson) | GIS corridor and stations |
| [`lubumbashi.design-quality.yaml`](lubumbashi.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
scripts/regenerate-city.sh lubumbashi
```
