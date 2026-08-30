# Chittagong — Urban Rail Network

**Country:** BD · **Population:** 5,200,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Chittagong-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$5.36 bn (85.2%) of external capital** and **$6.72 bn of external interest**. Capital plus saved interest totals **$12.08 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Chittagong rail network on OpenStreetMap](chittagong-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 8 / 103 / 15 |
| Route length | 323.8 km double track |
| Coverage / transfer reachability | 71.7% / 36% |
| Estimated station catchment | 3,728,400 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 517 × 6-car `metro-6car` trainsets (465 peak revenue) |
| Peak network throughput | 230,400 passengers/hour |
| Practical service capacity | 2,008,800 passenger-trips/day |
| Annual paid-trip planning range | 366.6–586.6 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 41.9 km | 13 | 78 | S Mid ↔ NW Outer |
| line-2 | 29.0 km | 12 | 57 | S Mid ↔ N Mid |
| line-3 | 47.6 km | 14 | 89 | N Mid ↔ S Outer |
| line-4 | 33.3 km | 11 | 61 | NE Outer ↔ SW Inner |
| line-5 | 35.8 km | 11 | 70 | SW Inner ↔ NE Outer |
| line-6 | 29.9 km | 10 | 59 | W Inner ↔ SE Mid |
| line-7 | 37.0 km | 11 | 71 | W Inner ↔ SE Outer |
| line-8 | 69.2 km | 21 | 32 | NW Mid ↔ NW Mid |
| **Total** | **323.8 km** | **103 unique** | **517** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 3,488 one-way journeys / 134,474 train-km/day |
| Annual traction demand | 1,272.2 GWh |
| Station/depot PV / storage | 31.1 MW / 214.0 MWh |
| Aggregate charging power | 176.0 MW |
| Dedicated solar plant | 799.3 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-7: 17.9 km / 269 kWh |
| Lowest traversal charging margin | line-4: 219 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.19 bn |
| Stations | $546 M |
| Depots | $8.0 M |
| Rolling stock | $869 M |
| Dedicated solar plant | $639 M |
| Residual train control | $16 M |
| Charging microgrids | $39 M |
| EPC / project services | $187 M |
| **Total city programme** | **$3.50 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $933 M (26.7%) |
| Domestic / local capital | $2.56 bn (73.3%) |
| Annual public construction commitment | $289 M / yr for 7 years |
| Annual post-grace debt service | $242 M / yr |
| External capital saved vs default turnkey sensitivity | $5.36 bn |
| Capital + lifetime external interest saved | $12.08 bn |
| Annual OPEX | $85 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 1,111 assets / 5,187 tasks | [`chittagong-operations-manifest.json`](operations/chittagong-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`chittagong.toml`](chittagong.toml) | Expanded simulator scenario |
| [`chittagong.corridor.geojson`](chittagong.corridor.geojson) | GIS corridor and stations |
| [`chittagong.design-quality.yaml`](chittagong.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh chittagong
```
