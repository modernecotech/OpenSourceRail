# Kumba — Urban Rail Network

**Country:** CM · **Population:** 400,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Kumba-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$521 M (86.1%) of external capital** and **$653 M of external interest**. Capital plus saved interest totals **$1.17 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Kumba rail network on OpenStreetMap](kumba-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 15 / 2 |
| Route length | 42.5 km double track |
| Coverage / transfer reachability | 68.4% / 100% |
| Estimated station catchment | 273,600 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 90 × 3-car `light-metro-3car` trainsets (81 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 20.2 km | 6 | 42 | S Mid ↔ NE Outer |
| line-2 | 12.8 km | 5 | 27 | W Outer ↔ E Inner |
| line-3 |  9.5 km | 4 | 21 | SE Mid ↔ NW Inner |
| **Total** | **42.5 km** | **15 unique** | **90** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 19,782 train-km/day |
| Annual traction demand | 93.6 GWh |
| Station/depot PV / storage | 8.9 MW / 46.5 MWh |
| Aggregate charging power | 7.0 MW |
| Dedicated solar plant | 51.2 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 11.2 km / 84 kWh |
| Lowest traversal charging margin | line-3: 36 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $113 M |
| Stations | $71 M |
| Depots | $8.0 M |
| Rolling stock | $81 M |
| Dedicated solar plant | $41 M |
| Residual train control | $2.1 M |
| Charging microgrids | $1.6 M |
| EPC / project services | $19 M |
| **Total city programme** | **$336 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $84 M (25.1%) |
| Domestic / local capital | $252 M (74.9%) |
| Annual public construction commitment | $28 M / yr for 7 years |
| Annual post-grace debt service | $23 M / yr |
| External capital saved vs default turnkey sensitivity | $521 M |
| Capital + lifetime external interest saved | $1.17 bn |
| Annual OPEX | $8.7 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 181 assets / 858 tasks | [`kumba-operations-manifest.json`](operations/kumba-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`kumba.toml`](kumba.toml) | Expanded simulator scenario |
| [`kumba.corridor.geojson`](kumba.corridor.geojson) | GIS corridor and stations |
| [`kumba.design-quality.yaml`](kumba.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh kumba
```
