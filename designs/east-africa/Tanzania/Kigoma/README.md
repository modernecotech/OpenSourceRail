# Kigoma — Urban Rail Network

**Country:** TZ · **Population:** 300,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Kigoma-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$402 M (87.4%) of external capital** and **$503 M of external interest**. Capital plus saved interest totals **$905 M**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Kigoma rail network on OpenStreetMap](kigoma-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 17 / 1 |
| Route length | 35.9 km double track |
| Coverage / transfer reachability | 76.7% / 100% |
| Estimated station catchment | 230,100 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 76 × 2-car `tram-2car` trainsets (68 peak revenue) |
| Peak network throughput | 28,800 passengers/hour |
| Practical service capacity | 267,840 passenger-trips/day |
| Annual paid-trip planning range | 48.9–78.2 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 12.3 km | 6 | 26 | SW Outer ↔ E Mid |
| line-2 | 14.7 km | 6 | 30 | SE Outer ↔ N Outer |
| line-3 |  8.9 km | 5 | 20 | N Mid ↔ S Mid |
| **Total** | **35.9 km** | **17 unique** | **76** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 16,706 train-km/day |
| Annual traction demand | 52.7 GWh |
| Station/depot PV / storage | 9.8 MW / 48.0 MWh |
| Aggregate charging power | 8.5 MW |
| Dedicated solar plant | 23.3 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 4.3 km / 22 kWh |
| Lowest traversal charging margin | line-1: 47 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $93 M |
| Stations | $74 M |
| Depots | $8.0 M |
| Rolling stock | $43 M |
| Dedicated solar plant | $19 M |
| Residual train control | $1.8 M |
| Charging microgrids | $1.9 M |
| EPC / project services | $15 M |
| **Total city programme** | **$255 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $58 M (22.7%) |
| Domestic / local capital | $197 M (77.3%) |
| Annual public construction commitment | $23 M / yr for 7 years |
| Annual post-grace debt service | $19 M / yr |
| External capital saved vs default turnkey sensitivity | $402 M |
| Capital + lifetime external interest saved | $905 M |
| Annual OPEX | $6.3 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 176 assets / 791 tasks | [`kigoma-operations-manifest.json`](operations/kigoma-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`kigoma.toml`](kigoma.toml) | Expanded simulator scenario |
| [`kigoma.corridor.geojson`](kigoma.corridor.geojson) | GIS corridor and stations |
| [`kigoma.design-quality.yaml`](kigoma.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
scripts/regenerate-city.sh kigoma
```
