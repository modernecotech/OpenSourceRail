# Najran — Urban Rail Network

**Country:** SA · **Population:** 500,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Najran-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$820 M (87.3%) of external capital** and **$1.01 bn of external interest**. Capital plus saved interest totals **$1.83 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Najran rail network on OpenStreetMap](najran-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 20 / 1 |
| Route length | 56.7 km double track |
| Coverage / transfer reachability | 46.5% / 33% |
| Estimated station catchment | 232,500 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 120 × 3-car `light-metro-3car` trainsets (108 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 21.4 km | 8 | 46 | SW Outer ↔ NE Mid |
| line-2 | 20.0 km | 6 | 42 | E Outer ↔ SW Outer |
| line-3 | 15.3 km | 6 | 32 | SE Mid ↔ N Outer |
| **Total** | **56.7 km** | **20 unique** | **120** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 26,368 train-km/day |
| Annual traction demand | 124.7 GWh |
| Station/depot PV / storage | 10.7 MW / 49.5 MWh |
| Aggregate charging power | 10.0 MW |
| Dedicated solar plant | 53.2 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 6.5 km / 53 kWh |
| Lowest traversal charging margin | line-3: 36 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $241 M |
| Stations | $86 M |
| Depots | $8.0 M |
| Rolling stock | $108 M |
| Dedicated solar plant | $43 M |
| Residual train control | $2.8 M |
| Charging microgrids | $2.2 M |
| EPC / project services | $31 M |
| **Total city programme** | **$522 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $119 M (22.9%) |
| Domestic / local capital | $402 M (77.1%) |
| Annual public construction commitment | $36 M / yr for 5 years |
| Annual post-grace debt service | $25 M / yr |
| External capital saved vs default turnkey sensitivity | $820 M |
| Capital + lifetime external interest saved | $1.83 bn |
| Annual OPEX | $21 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 242 assets / 1,151 tasks | [`najran-operations-manifest.json`](operations/najran-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`najran.toml`](najran.toml) | Expanded simulator scenario |
| [`najran.corridor.geojson`](najran.corridor.geojson) | GIS corridor and stations |
| [`najran.design-quality.yaml`](najran.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
scripts/regenerate-city.sh najran
```
