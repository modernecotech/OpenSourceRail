# Hillah — Urban Rail Network

**Country:** IQ · **Population:** 700,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Hillah-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$718 M (86.5%) of external capital** and **$883 M of external interest**. Capital plus saved interest totals **$1.60 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Hillah rail network on OpenStreetMap](hillah-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 24 / 1 |
| Route length | 57.9 km double track |
| Coverage / transfer reachability | 65.7% / 33% |
| Estimated station catchment | 459,900 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 125 × 3-car `light-metro-3car` trainsets (113 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 19.5 km | 8 | 42 | NE Mid ↔ S Outer |
| line-2 | 18.9 km | 8 | 41 | N Outer ↔ SW Mid |
| line-3 | 19.5 km | 8 | 42 | W Outer ↔ NE Mid |
| **Total** | **57.9 km** | **24 unique** | **125** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 26,907 train-km/day |
| Annual traction demand | 127.3 GWh |
| Station/depot PV / storage | 11.0 MW / 50.0 MWh |
| Aggregate charging power | 10.5 MW |
| Dedicated solar plant | 54.2 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 7.4 km / 60 kWh |
| Lowest traversal charging margin | line-3: 56 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $171 M |
| Stations | $94 M |
| Depots | $8.0 M |
| Rolling stock | $112 M |
| Dedicated solar plant | $43 M |
| Residual train control | $2.9 M |
| Charging microgrids | $2.3 M |
| EPC / project services | $27 M |
| **Total city programme** | **$461 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $112 M (24.2%) |
| Domestic / local capital | $349 M (75.8%) |
| Annual public construction commitment | $43 M / yr for 5 years |
| Annual post-grace debt service | $32 M / yr |
| External capital saved vs default turnkey sensitivity | $718 M |
| Capital + lifetime external interest saved | $1.60 bn |
| Annual OPEX | $13 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 265 assets / 1,238 tasks | [`hillah-operations-manifest.json`](operations/hillah-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`hillah.toml`](hillah.toml) | Expanded simulator scenario |
| [`hillah.corridor.geojson`](hillah.corridor.geojson) | GIS corridor and stations |
| [`hillah.design-quality.yaml`](hillah.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
scripts/regenerate-city.sh hillah
```
