# Machakos — Urban Rail Network

**Country:** KE · **Population:** 300,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Machakos-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$374 M (88.1%) of external capital** and **$469 M of external interest**. Capital plus saved interest totals **$842 M**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Machakos rail network on OpenStreetMap](machakos-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 14 / 1 |
| Route length | 28.9 km double track |
| Coverage / transfer reachability | 76.2% / 100% |
| Estimated station catchment | 228,600 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 63 × 2-car `tram-2car` trainsets (56 peak revenue) |
| Peak network throughput | 28,800 passengers/hour |
| Practical service capacity | 267,840 passenger-trips/day |
| Annual paid-trip planning range | 48.9–78.2 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 12.2 km | 5 | 26 | N Outer ↔ S Mid |
| line-2 |  7.6 km | 4 | 17 | SE Mid ↔ W Mid |
| line-3 |  9.1 km | 5 | 20 | N Mid ↔ W Mid |
| **Total** | **28.9 km** | **14 unique** | **63** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 13,430 train-km/day |
| Annual traction demand | 42.4 GWh |
| Station/depot PV / storage | 8.9 MW / 46.5 MWh |
| Aggregate charging power | 7.0 MW |
| Dedicated solar plant | 10.3 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 6.5 km / 36 kWh |
| Lowest traversal charging margin | line-2: 35 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $88 M |
| Stations | $78 M |
| Depots | $8.0 M |
| Rolling stock | $35 M |
| Dedicated solar plant | $8.2 M |
| Residual train control | $1.4 M |
| Charging microgrids | $1.6 M |
| EPC / project services | $15 M |
| **Total city programme** | **$236 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $51 M (21.4%) |
| Domestic / local capital | $185 M (78.6%) |
| Annual public construction commitment | $25 M / yr for 7 years |
| Annual post-grace debt service | $20 M / yr |
| External capital saved vs default turnkey sensitivity | $374 M |
| Capital + lifetime external interest saved | $842 M |
| Annual OPEX | $6.0 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 147 assets / 654 tasks | [`machakos-operations-manifest.json`](operations/machakos-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`machakos.toml`](machakos.toml) | Expanded simulator scenario |
| [`machakos.corridor.geojson`](machakos.corridor.geojson) | GIS corridor and stations |
| [`machakos.design-quality.yaml`](machakos.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
scripts/regenerate-city.sh machakos
```
