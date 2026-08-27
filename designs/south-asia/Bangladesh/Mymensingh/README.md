# Mymensingh — Urban Rail Network

**Country:** BD · **Population:** 700,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Mymensingh-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$723 M (87.5%) of external capital** and **$907 M of external interest**. Capital plus saved interest totals **$1.63 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Mymensingh rail network on OpenStreetMap](mymensingh-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 17 / 1 |
| Route length | 42.3 km double track |
| Coverage / transfer reachability | 43.4% / 100% |
| Estimated station catchment | 303,800 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 92 × 3-car `light-metro-3car` trainsets (82 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 11.6 km | 5 | 26 | W Mid ↔ S Mid |
| line-2 | 11.0 km | 5 | 24 | W Mid ↔ NE Inner |
| line-3 | 19.7 km | 7 | 42 | NE Outer ↔ SW Mid |
| **Total** | **42.3 km** | **17 unique** | **92** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 19,675 train-km/day |
| Annual traction demand | 93.1 GWh |
| Station/depot PV / storage | 9.2 MW / 47.0 MWh |
| Aggregate charging power | 7.5 MW |
| Dedicated solar plant | 50.5 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 12.7 km / 95 kWh |
| Lowest traversal charging margin | line-2: 32 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $227 M |
| Stations | $70 M |
| Depots | $8.0 M |
| Rolling stock | $83 M |
| Dedicated solar plant | $40 M |
| Residual train control | $2.1 M |
| Charging microgrids | $1.6 M |
| EPC / project services | $27 M |
| **Total city programme** | **$459 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $103 M (22.4%) |
| Domestic / local capital | $356 M (77.6%) |
| Annual public construction commitment | $39 M / yr for 7 years |
| Annual post-grace debt service | $32 M / yr |
| External capital saved vs default turnkey sensitivity | $723 M |
| Capital + lifetime external interest saved | $1.63 bn |
| Annual OPEX | $11 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 192 assets / 899 tasks | [`mymensingh-operations-manifest.json`](operations/mymensingh-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`mymensingh.toml`](mymensingh.toml) | Expanded simulator scenario |
| [`mymensingh.corridor.geojson`](mymensingh.corridor.geojson) | GIS corridor and stations |
| [`mymensingh.design-quality.yaml`](mymensingh.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
scripts/regenerate-city.sh mymensingh
```
