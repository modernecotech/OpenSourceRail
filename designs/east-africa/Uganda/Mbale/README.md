# Mbale — Urban Rail Network

**Country:** UG · **Population:** 300,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Mbale-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$396 M (87.8%) of external capital** and **$497 M of external interest**. Capital plus saved interest totals **$893 M**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Mbale rail network on OpenStreetMap](mbale-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 13 / 1 |
| Route length | 34.1 km double track |
| Coverage / transfer reachability | 84.7% / 33% |
| Estimated station catchment | 254,100 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 71 × 2-car `tram-2car` trainsets (63 peak revenue) |
| Peak network throughput | 28,800 passengers/hour |
| Practical service capacity | 267,840 passenger-trips/day |
| Annual paid-trip planning range | 48.9–78.2 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 14.5 km | 6 | 30 | S Outer ↔ N Mid |
| line-2 | 14.4 km | 4 | 28 | NE Outer ↔ S Mid |
| line-3 |  5.2 km | 3 | 13 | E Inner ↔ NW Inner |
| **Total** | **34.1 km** | **13 unique** | **71** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 15,877 train-km/day |
| Annual traction demand | 50.1 GWh |
| Station/depot PV / storage | 8.6 MW / 46.0 MWh |
| Aggregate charging power | 6.5 MW |
| Dedicated solar plant | 23.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 6.2 km / 31 kWh |
| Lowest traversal charging margin | line-2: 35 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $117 M |
| Stations | $49 M |
| Depots | $8.0 M |
| Rolling stock | $40 M |
| Dedicated solar plant | $18 M |
| Residual train control | $1.7 M |
| Charging microgrids | $1.4 M |
| EPC / project services | $15 M |
| **Total city programme** | **$251 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $55 M (22.0%) |
| Domestic / local capital | $196 M (78.0%) |
| Annual public construction commitment | $30 M / yr for 7 years |
| Annual post-grace debt service | $25 M / yr |
| External capital saved vs default turnkey sensitivity | $396 M |
| Capital + lifetime external interest saved | $893 M |
| Annual OPEX | $6.0 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 150 assets / 695 tasks | [`mbale-operations-manifest.json`](operations/mbale-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`mbale.toml`](mbale.toml) | Expanded simulator scenario |
| [`mbale.corridor.geojson`](mbale.corridor.geojson) | GIS corridor and stations |
| [`mbale.design-quality.yaml`](mbale.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
scripts/regenerate-city.sh mbale
```
