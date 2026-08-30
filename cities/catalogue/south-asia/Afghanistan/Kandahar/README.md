# Kandahar — Urban Rail Network

**Country:** AF · **Population:** 700,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Kandahar-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$687 M (86.6%) of external capital** and **$887 M of external interest**. Capital plus saved interest totals **$1.57 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Kandahar rail network on OpenStreetMap](kandahar-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 21 / 1 |
| Route length | 52.9 km double track |
| Coverage / transfer reachability | 67.7% / 100% |
| Estimated station catchment | 473,900 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 113 × 3-car `light-metro-3car` trainsets (101 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 23.1 km | 9 | 48 | NE Outer ↔ W Outer |
| line-2 | 16.5 km | 7 | 36 | SE Outer ↔ N Mid |
| line-3 | 13.3 km | 5 | 29 | SW Mid ↔ E Mid |
| **Total** | **52.9 km** | **21 unique** | **113** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 24,593 train-km/day |
| Annual traction demand | 116.3 GWh |
| Station/depot PV / storage | 11.0 MW / 50.0 MWh |
| Aggregate charging power | 10.5 MW |
| Dedicated solar plant | 48.4 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 5.8 km / 47 kWh |
| Lowest traversal charging margin | line-3: 46 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $150 M |
| Stations | $111 M |
| Depots | $8.0 M |
| Rolling stock | $102 M |
| Dedicated solar plant | $39 M |
| Residual train control | $2.6 M |
| Charging microgrids | $2.4 M |
| EPC / project services | $26 M |
| **Total city programme** | **$440 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $106 M (24.0%) |
| Domestic / local capital | $334 M (76.0%) |
| Annual public construction commitment | $60 M / yr for 10 years |
| Annual post-grace debt service | $55 M / yr |
| External capital saved vs default turnkey sensitivity | $687 M |
| Capital + lifetime external interest saved | $1.57 bn |
| Annual OPEX | $11 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 239 assets / 1,116 tasks | [`kandahar-operations-manifest.json`](operations/kandahar-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`kandahar.toml`](kandahar.toml) | Expanded simulator scenario |
| [`kandahar.corridor.geojson`](kandahar.corridor.geojson) | GIS corridor and stations |
| [`kandahar.design-quality.yaml`](kandahar.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh kandahar
```
