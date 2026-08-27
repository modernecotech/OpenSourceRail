# Zarqa — Urban Rail Network

**Country:** JO · **Population:** 700,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Zarqa-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$1.12 bn (86.6%) of external capital** and **$1.38 bn of external interest**. Capital plus saved interest totals **$2.51 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Zarqa rail network on OpenStreetMap](zarqa-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 24 / 2 |
| Route length | 72.5 km double track |
| Coverage / transfer reachability | 55.8% / 100% |
| Estimated station catchment | 390,600 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 227 × 3-car `light-metro-3car` trainsets (205 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 29.7 km | 10 | 93 | NE Outer ↔ SW Outer |
| line-2 | 27.9 km | 9 | 86 | SW Outer ↔ NE Outer |
| line-3 | 15.0 km | 5 | 48 | N Mid ↔ E Mid |
| **Total** | **72.5 km** | **24 unique** | **227** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 33,729 train-km/day |
| Annual traction demand | 159.6 GWh |
| Station/depot PV / storage | 10.7 MW / 49.5 MWh |
| Aggregate charging power | 10.0 MW |
| Dedicated solar plant | 71.5 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 10.6 km / 85 kWh |
| Lowest traversal charging margin | line-3: 51 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $307 M |
| Stations | $95 M |
| Depots | $8.0 M |
| Rolling stock | $204 M |
| Dedicated solar plant | $57 M |
| Residual train control | $3.6 M |
| Charging microgrids | $2.2 M |
| EPC / project services | $43 M |
| **Total city programme** | **$721 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $174 M (24.1%) |
| Domestic / local capital | $548 M (75.9%) |
| Annual public construction commitment | $63 M / yr for 5 years |
| Annual post-grace debt service | $46 M / yr |
| External capital saved vs default turnkey sensitivity | $1.12 bn |
| Capital + lifetime external interest saved | $2.51 bn |
| Annual OPEX | $22 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 383 assets / 1,966 tasks | [`zarqa-operations-manifest.json`](operations/zarqa-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`zarqa.toml`](zarqa.toml) | Expanded simulator scenario |
| [`zarqa.corridor.geojson`](zarqa.corridor.geojson) | GIS corridor and stations |
| [`zarqa.design-quality.yaml`](zarqa.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
scripts/regenerate-city.sh zarqa
```
