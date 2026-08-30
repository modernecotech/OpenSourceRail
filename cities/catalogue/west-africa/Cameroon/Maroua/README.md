# Maroua — Urban Rail Network

**Country:** CM · **Population:** 500,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Maroua-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$710 M (87.0%) of external capital** and **$890 M of external interest**. Capital plus saved interest totals **$1.60 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Maroua rail network on OpenStreetMap](maroua-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 21 / 1 |
| Route length | 52.5 km double track |
| Coverage / transfer reachability | 73.5% / 100% |
| Estimated station catchment | 367,500 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 113 × 3-car `light-metro-3car` trainsets (101 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 26.4 km | 9 | 54 | NE Outer ↔ SW Outer |
| line-2 | 15.7 km | 6 | 35 | N Inner ↔ SW Outer |
| line-3 | 10.5 km | 6 | 24 | W Inner ↔ E Mid |
| **Total** | **52.5 km** | **21 unique** | **113** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 24,424 train-km/day |
| Annual traction demand | 115.5 GWh |
| Station/depot PV / storage | 10.4 MW / 49.0 MWh |
| Aggregate charging power | 9.5 MW |
| Dedicated solar plant | 44.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 8.0 km / 67 kWh |
| Lowest traversal charging margin | line-3: 35 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $183 M |
| Stations | $94 M |
| Depots | $8.0 M |
| Rolling stock | $102 M |
| Dedicated solar plant | $35 M |
| Residual train control | $2.6 M |
| Charging microgrids | $2.1 M |
| EPC / project services | $27 M |
| **Total city programme** | **$453 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $106 M (23.3%) |
| Domestic / local capital | $348 M (76.7%) |
| Annual public construction commitment | $38 M / yr for 7 years |
| Annual post-grace debt service | $32 M / yr |
| External capital saved vs default turnkey sensitivity | $710 M |
| Capital + lifetime external interest saved | $1.60 bn |
| Annual OPEX | $11 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 237 assets / 1,110 tasks | [`maroua-operations-manifest.json`](operations/maroua-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`maroua.toml`](maroua.toml) | Expanded simulator scenario |
| [`maroua.corridor.geojson`](maroua.corridor.geojson) | GIS corridor and stations |
| [`maroua.design-quality.yaml`](maroua.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh maroua
```
