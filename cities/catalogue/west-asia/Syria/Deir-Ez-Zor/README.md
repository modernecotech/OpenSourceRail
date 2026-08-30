# Deir-Ez-Zor — Urban Rail Network

**Country:** SY · **Population:** 500,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Deir-Ez-Zor-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$759 M (86.7%) of external capital** and **$980 M of external interest**. Capital plus saved interest totals **$1.74 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Deir-Ez-Zor rail network on OpenStreetMap](deir-ez-zor-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 18 / 1 |
| Route length | 51.4 km double track |
| Coverage / transfer reachability | 64.8% / 100% |
| Estimated station catchment | 324,000 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 143 × 3-car `light-metro-3car` trainsets (128 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 21.7 km | 7 | 59 | NW Outer ↔ SE Outer |
| line-2 | 13.4 km | 5 | 38 | N Mid ↔ SW Mid |
| line-3 | 16.3 km | 6 | 46 | NE Outer ↔ SW Mid |
| **Total** | **51.4 km** | **18 unique** | **143** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 23,885 train-km/day |
| Annual traction demand | 113.0 GWh |
| Station/depot PV / storage | 9.2 MW / 47.0 MWh |
| Aggregate charging power | 7.5 MW |
| Dedicated solar plant | 48.7 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 10.4 km / 84 kWh |
| Lowest traversal charging margin | line-3: 35 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $195 M |
| Stations | $82 M |
| Depots | $8.0 M |
| Rolling stock | $129 M |
| Dedicated solar plant | $39 M |
| Residual train control | $2.6 M |
| Charging microgrids | $1.7 M |
| EPC / project services | $29 M |
| **Total city programme** | **$486 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $117 M (24.0%) |
| Domestic / local capital | $370 M (76.0%) |
| Annual public construction commitment | $72 M / yr for 10 years |
| Annual post-grace debt service | $67 M / yr |
| External capital saved vs default turnkey sensitivity | $759 M |
| Capital + lifetime external interest saved | $1.74 bn |
| Annual OPEX | $12 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 256 assets / 1,277 tasks | [`deir-ez-zor-operations-manifest.json`](operations/deir-ez-zor-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`deir-ez-zor.toml`](deir-ez-zor.toml) | Expanded simulator scenario |
| [`deir-ez-zor.corridor.geojson`](deir-ez-zor.corridor.geojson) | GIS corridor and stations |
| [`deir-ez-zor.design-quality.yaml`](deir-ez-zor.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh deir-ez-zor
```
