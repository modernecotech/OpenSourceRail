# Luxor — Urban Rail Network

**Country:** EG · **Population:** 500,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Luxor-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$648 M (86.6%) of external capital** and **$796 M of external interest**. Capital plus saved interest totals **$1.44 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Luxor rail network on OpenStreetMap](luxor-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 19 / 2 |
| Route length | 50.7 km double track |
| Coverage / transfer reachability | 72.7% / 100% |
| Estimated station catchment | 363,500 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 111 × 3-car `light-metro-3car` trainsets (99 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 13.2 km | 5 | 29 | N Mid ↔ S Inner |
| line-2 | 20.8 km | 8 | 46 | SW Outer ↔ NE Mid |
| line-3 | 16.7 km | 6 | 36 | E Mid ↔ N Mid |
| **Total** | **50.7 km** | **19 unique** | **111** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 23,558 train-km/day |
| Annual traction demand | 111.4 GWh |
| Station/depot PV / storage | 9.8 MW / 48.0 MWh |
| Aggregate charging power | 8.5 MW |
| Dedicated solar plant | 47.2 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 11.0 km / 89 kWh |
| Lowest traversal charging margin | line-1: 46 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $145 M |
| Stations | $96 M |
| Depots | $8.0 M |
| Rolling stock | $100 M |
| Dedicated solar plant | $38 M |
| Residual train control | $2.5 M |
| Charging microgrids | $1.9 M |
| EPC / project services | $25 M |
| **Total city programme** | **$416 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $101 M (24.2%) |
| Domestic / local capital | $315 M (75.8%) |
| Annual public construction commitment | $44 M / yr for 5 years |
| Annual post-grace debt service | $33 M / yr |
| External capital saved vs default turnkey sensitivity | $648 M |
| Capital + lifetime external interest saved | $1.44 bn |
| Annual OPEX | $11 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 225 assets / 1,066 tasks | [`luxor-operations-manifest.json`](operations/luxor-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`luxor.toml`](luxor.toml) | Expanded simulator scenario |
| [`luxor.corridor.geojson`](luxor.corridor.geojson) | GIS corridor and stations |
| [`luxor.design-quality.yaml`](luxor.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh luxor
```
