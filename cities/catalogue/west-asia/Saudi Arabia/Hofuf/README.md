# Hofuf — Urban Rail Network

**Country:** SA · **Population:** 800,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Hofuf-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$872 M (86.2%) of external capital** and **$1.07 bn of external interest**. Capital plus saved interest totals **$1.94 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Hofuf rail network on OpenStreetMap](hofuf-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 26 / 1 |
| Route length | 77.9 km double track |
| Coverage / transfer reachability | 49.3% / 100% |
| Estimated station catchment | 394,400 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 163 × 3-car `light-metro-3car` trainsets (147 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 25.9 km | 8 | 53 | NW Outer ↔ S Outer |
| line-2 | 26.7 km | 9 | 58 | SW Outer ↔ NE Outer |
| line-3 | 25.3 km | 9 | 52 | N Outer ↔ SE Outer |
| **Total** | **77.9 km** | **26 unique** | **163** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 36,201 train-km/day |
| Annual traction demand | 171.2 GWh |
| Station/depot PV / storage | 12.5 MW / 52.5 MWh |
| Aggregate charging power | 13.0 MW |
| Dedicated solar plant | 75.5 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 6.9 km / 56 kWh |
| Lowest traversal charging margin | line-1: 64 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $203 M |
| Stations | $104 M |
| Depots | $8.0 M |
| Rolling stock | $147 M |
| Dedicated solar plant | $60 M |
| Residual train control | $3.9 M |
| Charging microgrids | $2.8 M |
| EPC / project services | $33 M |
| **Total city programme** | **$562 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $140 M (24.9%) |
| Domestic / local capital | $422 M (75.1%) |
| Annual public construction commitment | $38 M / yr for 5 years |
| Annual post-grace debt service | $27 M / yr |
| External capital saved vs default turnkey sensitivity | $872 M |
| Capital + lifetime external interest saved | $1.94 bn |
| Annual OPEX | $25 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 321 assets / 1,548 tasks | [`hofuf-operations-manifest.json`](operations/hofuf-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`hofuf.toml`](hofuf.toml) | Expanded simulator scenario |
| [`hofuf.corridor.geojson`](hofuf.corridor.geojson) | GIS corridor and stations |
| [`hofuf.design-quality.yaml`](hofuf.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh hofuf
```
