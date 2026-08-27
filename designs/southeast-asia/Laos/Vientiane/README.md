# Vientiane — Urban Rail Network

**Country:** LA · **Population:** 948,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Vientiane-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$907 M (86.1%) of external capital** and **$1.14 bn of external interest**. Capital plus saved interest totals **$2.04 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Vientiane rail network on OpenStreetMap](vientiane-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 27 / 1 |
| Route length | 74.4 km double track |
| Coverage / transfer reachability | 49.6% / 100% |
| Estimated station catchment | 470,208 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 155 × 3-car `light-metro-3car` trainsets (139 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 23.3 km | 9 | 48 | NE Outer ↔ S Outer |
| line-2 | 23.2 km | 9 | 48 | NE Outer ↔ SW Mid |
| line-3 | 27.8 km | 9 | 59 | NW Outer ↔ SE Outer |
| **Total** | **74.4 km** | **27 unique** | **155** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 34,596 train-km/day |
| Annual traction demand | 163.7 GWh |
| Station/depot PV / storage | 12.5 MW / 52.5 MWh |
| Aggregate charging power | 13.0 MW |
| Dedicated solar plant | 93.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 7.0 km / 53 kWh |
| Lowest traversal charging margin | line-1: 65 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $211 M |
| Stations | $113 M |
| Depots | $8.0 M |
| Rolling stock | $140 M |
| Dedicated solar plant | $74 M |
| Residual train control | $3.7 M |
| Charging microgrids | $2.8 M |
| EPC / project services | $33 M |
| **Total city programme** | **$585 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $146 M (25.0%) |
| Domestic / local capital | $439 M (75.0%) |
| Annual public construction commitment | $56 M / yr for 7 years |
| Annual post-grace debt service | $47 M / yr |
| External capital saved vs default turnkey sensitivity | $907 M |
| Capital + lifetime external interest saved | $2.04 bn |
| Annual OPEX | $15 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 317 assets / 1,504 tasks | [`vientiane-operations-manifest.json`](operations/vientiane-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`vientiane.toml`](vientiane.toml) | Expanded simulator scenario |
| [`vientiane.corridor.geojson`](vientiane.corridor.geojson) | GIS corridor and stations |
| [`vientiane.design-quality.yaml`](vientiane.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
scripts/regenerate-city.sh vientiane
```
