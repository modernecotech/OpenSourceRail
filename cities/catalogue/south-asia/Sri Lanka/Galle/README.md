# Galle — Urban Rail Network

**Country:** LK · **Population:** 500,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Galle-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$842 M (85.7%) of external capital** and **$1.06 bn of external interest**. Capital plus saved interest totals **$1.90 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Galle rail network on OpenStreetMap](galle-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 23 / 1 |
| Route length | 63.7 km double track |
| Coverage / transfer reachability | 53.7% / 100% |
| Estimated station catchment | 268,500 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 177 × 3-car `light-metro-3car` trainsets (160 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 22.4 km | 9 | 61 | SE Outer ↔ W Outer |
| line-2 | 22.7 km | 6 | 62 | NW Outer ↔ SE Outer |
| line-3 | 18.6 km | 8 | 54 | NE Outer ↔ W Mid |
| **Total** | **63.7 km** | **23 unique** | **177** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 29,613 train-km/day |
| Annual traction demand | 140.1 GWh |
| Station/depot PV / storage | 10.7 MW / 49.5 MWh |
| Aggregate charging power | 10.0 MW |
| Dedicated solar plant | 79.6 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 10.5 km / 78 kWh |
| Lowest traversal charging margin | line-3: 67 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $183 M |
| Stations | $95 M |
| Depots | $8.0 M |
| Rolling stock | $159 M |
| Dedicated solar plant | $64 M |
| Residual train control | $3.2 M |
| Charging microgrids | $2.2 M |
| EPC / project services | $32 M |
| **Total city programme** | **$546 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $140 M (25.7%) |
| Domestic / local capital | $406 M (74.3%) |
| Annual public construction commitment | $62 M / yr for 7 years |
| Annual post-grace debt service | $53 M / yr |
| External capital saved vs default turnkey sensitivity | $842 M |
| Capital + lifetime external interest saved | $1.90 bn |
| Annual OPEX | $15 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 320 assets / 1,595 tasks | [`galle-operations-manifest.json`](operations/galle-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`galle.toml`](galle.toml) | Expanded simulator scenario |
| [`galle.corridor.geojson`](galle.corridor.geojson) | GIS corridor and stations |
| [`galle.design-quality.yaml`](galle.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh galle
```
