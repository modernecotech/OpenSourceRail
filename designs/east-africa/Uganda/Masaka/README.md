# Masaka — Urban Rail Network

**Country:** UG · **Population:** 250,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Masaka-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$411 M (87.7%) of external capital** and **$515 M of external interest**. Capital plus saved interest totals **$927 M**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Masaka rail network on OpenStreetMap](masaka-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 16 / 1 |
| Route length | 32.1 km double track |
| Coverage / transfer reachability | 55.8% / 100% |
| Estimated station catchment | 139,500 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 69 × 2-car `tram-2car` trainsets (61 peak revenue) |
| Peak network throughput | 28,800 passengers/hour |
| Practical service capacity | 267,840 passenger-trips/day |
| Annual paid-trip planning range | 48.9–78.2 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 10.1 km | 6 | 24 | NE Mid ↔ W Mid |
| line-2 |  9.8 km | 4 | 20 | S Mid ↔ E Mid |
| line-3 | 12.1 km | 6 | 25 | SE Mid ↔ NW Outer |
| **Total** | **32.1 km** | **16 unique** | **69** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 14,907 train-km/day |
| Annual traction demand | 47.0 GWh |
| Station/depot PV / storage | 9.5 MW / 47.5 MWh |
| Aggregate charging power | 8.0 MW |
| Dedicated solar plant | 19.9 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 3.7 km / 19 kWh |
| Lowest traversal charging margin | line-2: 36 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $95 M |
| Stations | $83 M |
| Depots | $8.0 M |
| Rolling stock | $39 M |
| Dedicated solar plant | $16 M |
| Residual train control | $1.6 M |
| Charging microgrids | $1.8 M |
| EPC / project services | $16 M |
| **Total city programme** | **$260 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $58 M (22.1%) |
| Domestic / local capital | $203 M (77.9%) |
| Annual public construction commitment | $31 M / yr for 7 years |
| Annual post-grace debt service | $26 M / yr |
| External capital saved vs default turnkey sensitivity | $411 M |
| Capital + lifetime external interest saved | $927 M |
| Annual OPEX | $6.2 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 164 assets / 727 tasks | [`masaka-operations-manifest.json`](operations/masaka-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`masaka.toml`](masaka.toml) | Expanded simulator scenario |
| [`masaka.corridor.geojson`](masaka.corridor.geojson) | GIS corridor and stations |
| [`masaka.design-quality.yaml`](masaka.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
scripts/regenerate-city.sh masaka
```
