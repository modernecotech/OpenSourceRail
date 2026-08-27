# Gulu — Urban Rail Network

**Country:** UG · **Population:** 350,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Gulu-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$682 M (85.5%) of external capital** and **$855 M of external interest**. Capital plus saved interest totals **$1.54 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Gulu rail network on OpenStreetMap](gulu-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 18 / 1 |
| Route length | 60.1 km double track |
| Coverage / transfer reachability | 67.9% / 33% |
| Estimated station catchment | 237,650 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 139 × 3-car `light-metro-3car` trainsets (125 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 14.9 km | 5 | 36 | SW Mid ↔ NE Mid |
| line-2 | 28.7 km | 8 | 65 | SE Outer ↔ NW Outer |
| line-3 | 16.4 km | 5 | 38 | W Outer ↔ NE Mid |
| **Total** | **60.1 km** | **18 unique** | **139** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 27,927 train-km/day |
| Annual traction demand | 132.1 GWh |
| Station/depot PV / storage | 8.9 MW / 53.0 MWh |
| Aggregate charging power | 14.0 MW |
| Dedicated solar plant | 76.5 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 12.4 km / 93 kWh |
| Lowest traversal charging margin | line-3: 61 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $157 M |
| Stations | $61 M |
| Depots | $8.0 M |
| Rolling stock | $125 M |
| Dedicated solar plant | $61 M |
| Residual train control | $3.0 M |
| Charging microgrids | $3.1 M |
| EPC / project services | $25 M |
| **Total city programme** | **$443 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $116 M (26.1%) |
| Domestic / local capital | $328 M (73.9%) |
| Annual public construction commitment | $51 M / yr for 7 years |
| Annual post-grace debt service | $44 M / yr |
| External capital saved vs default turnkey sensitivity | $682 M |
| Capital + lifetime external interest saved | $1.54 bn |
| Annual OPEX | $11 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 249 assets / 1,244 tasks | [`gulu-operations-manifest.json`](operations/gulu-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`gulu.toml`](gulu.toml) | Expanded simulator scenario |
| [`gulu.corridor.geojson`](gulu.corridor.geojson) | GIS corridor and stations |
| [`gulu.design-quality.yaml`](gulu.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
scripts/regenerate-city.sh gulu
```
