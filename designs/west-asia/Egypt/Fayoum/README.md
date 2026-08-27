# Fayoum — Urban Rail Network

**Country:** EG · **Population:** 500,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Fayoum-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$823 M (85.7%) of external capital** and **$1.01 bn of external interest**. Capital plus saved interest totals **$1.83 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Fayoum rail network on OpenStreetMap](fayoum-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 23 / 1 |
| Route length | 68.8 km double track |
| Coverage / transfer reachability | 71.3% / 100% |
| Estimated station catchment | 356,500 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 190 × 3-car `light-metro-3car` trainsets (171 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 28.5 km | 9 | 78 | NW Outer ↔ SE Outer |
| line-2 | 18.8 km | 8 | 54 | E Outer ↔ NW Mid |
| line-3 | 21.5 km | 6 | 58 | SW Outer ↔ NE Outer |
| **Total** | **68.8 km** | **23 unique** | **190** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 31,969 train-km/day |
| Annual traction demand | 151.2 GWh |
| Station/depot PV / storage | 10.7 MW / 49.5 MWh |
| Aggregate charging power | 10.0 MW |
| Dedicated solar plant | 67.1 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 9.3 km / 75 kWh |
| Lowest traversal charging margin | line-3: 55 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $179 M |
| Stations | $85 M |
| Depots | $8.0 M |
| Rolling stock | $171 M |
| Dedicated solar plant | $54 M |
| Residual train control | $3.4 M |
| Charging microgrids | $2.1 M |
| EPC / project services | $31 M |
| **Total city programme** | **$533 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $137 M (25.7%) |
| Domestic / local capital | $396 M (74.3%) |
| Annual public construction commitment | $55 M / yr for 5 years |
| Annual post-grace debt service | $42 M / yr |
| External capital saved vs default turnkey sensitivity | $823 M |
| Capital + lifetime external interest saved | $1.83 bn |
| Annual OPEX | $15 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 334 assets / 1,687 tasks | [`fayoum-operations-manifest.json`](operations/fayoum-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`fayoum.toml`](fayoum.toml) | Expanded simulator scenario |
| [`fayoum.corridor.geojson`](fayoum.corridor.geojson) | GIS corridor and stations |
| [`fayoum.design-quality.yaml`](fayoum.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
scripts/regenerate-city.sh fayoum
```
