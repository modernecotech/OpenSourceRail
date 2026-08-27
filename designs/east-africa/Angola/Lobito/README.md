# Lobito — Urban Rail Network

**Country:** AO · **Population:** 500,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Lobito-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$466 M (86.6%) of external capital** and **$573 M of external interest**. Capital plus saved interest totals **$1.04 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Lobito rail network on OpenStreetMap](lobito-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 15 / 1 |
| Route length | 38.1 km double track |
| Coverage / transfer reachability | 71.5% / 100% |
| Estimated station catchment | 357,500 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 83 × 3-car `light-metro-3car` trainsets (74 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 18.3 km | 7 | 40 | S Outer ↔ NE Mid |
| line-2 | 11.6 km | 4 | 25 | SW Inner ↔ E Mid |
| line-3 |  8.1 km | 4 | 18 | SE Inner ↔ W Inner |
| **Total** | **38.1 km** | **15 unique** | **83** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 17,696 train-km/day |
| Annual traction demand | 83.7 GWh |
| Station/depot PV / storage | 9.2 MW / 47.0 MWh |
| Aggregate charging power | 7.5 MW |
| Dedicated solar plant | 30.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 6.3 km / 53 kWh |
| Lowest traversal charging margin | line-3: 23 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $101 M |
| Stations | $70 M |
| Depots | $8.0 M |
| Rolling stock | $75 M |
| Dedicated solar plant | $24 M |
| Residual train control | $1.9 M |
| Charging microgrids | $1.6 M |
| EPC / project services | $18 M |
| **Total city programme** | **$299 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $72 M (24.2%) |
| Domestic / local capital | $227 M (75.8%) |
| Annual public construction commitment | $33 M / yr for 5 years |
| Annual post-grace debt service | $25 M / yr |
| External capital saved vs default turnkey sensitivity | $466 M |
| Capital + lifetime external interest saved | $1.04 bn |
| Annual OPEX | $8.2 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 174 assets / 811 tasks | [`lobito-operations-manifest.json`](operations/lobito-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`lobito.toml`](lobito.toml) | Expanded simulator scenario |
| [`lobito.corridor.geojson`](lobito.corridor.geojson) | GIS corridor and stations |
| [`lobito.design-quality.yaml`](lobito.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
scripts/regenerate-city.sh lobito
```
