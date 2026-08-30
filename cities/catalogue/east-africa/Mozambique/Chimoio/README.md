# Chimoio — Urban Rail Network

**Country:** MZ · **Population:** 400,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Chimoio-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$452 M (86.2%) of external capital** and **$584 M of external interest**. Capital plus saved interest totals **$1.04 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Chimoio rail network on OpenStreetMap](chimoio-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 2 / 12 / 2 |
| Route length | 34.1 km double track |
| Coverage / transfer reachability | 55.7% / 100% |
| Estimated station catchment | 222,800 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 82 × 3-car `light-metro-3car` trainsets (73 peak revenue) |
| Peak network throughput | 28,800 passengers/hour |
| Practical service capacity | 267,840 passenger-trips/day |
| Annual paid-trip planning range | 48.9–78.2 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 20.0 km | 7 | 47 | E Outer ↔ SW Outer |
| line-2 | 14.2 km | 5 | 35 | E Outer ↔ W Mid |
| **Total** | **34.1 km** | **12 unique** | **82** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 930 one-way journeys / 15,875 train-km/day |
| Annual traction demand | 75.1 GWh |
| Station/depot PV / storage | 7.7 MW / 44.5 MWh |
| Aggregate charging power | 5.0 MW |
| Dedicated solar plant | 40.4 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 7.0 km / 52 kWh |
| Lowest traversal charging margin | line-2: 47 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $104 M |
| Stations | $54 M |
| Depots | $8.0 M |
| Rolling stock | $74 M |
| Dedicated solar plant | $32 M |
| Residual train control | $1.7 M |
| Charging microgrids | $1.2 M |
| EPC / project services | $17 M |
| **Total city programme** | **$291 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $73 M (24.9%) |
| Domestic / local capital | $219 M (75.1%) |
| Annual public construction commitment | $31 M / yr for 10 years |
| Annual post-grace debt service | $29 M / yr |
| External capital saved vs default turnkey sensitivity | $452 M |
| Capital + lifetime external interest saved | $1.04 bn |
| Annual OPEX | $7.3 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 157 assets / 757 tasks | [`chimoio-operations-manifest.json`](operations/chimoio-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`chimoio.toml`](chimoio.toml) | Expanded simulator scenario |
| [`chimoio.corridor.geojson`](chimoio.corridor.geojson) | GIS corridor and stations |
| [`chimoio.design-quality.yaml`](chimoio.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh chimoio
```
