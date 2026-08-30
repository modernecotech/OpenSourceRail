# Sukkur — Urban Rail Network

**Country:** PK · **Population:** 600,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Sukkur-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$842 M (88.4%) of external capital** and **$1.06 bn of external interest**. Capital plus saved interest totals **$1.90 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Sukkur rail network on OpenStreetMap](sukkur-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 15 / 1 |
| Route length | 43.7 km double track |
| Coverage / transfer reachability | 71.5% / 100% |
| Estimated station catchment | 429,000 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 92 × 3-car `light-metro-3car` trainsets (82 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 20.4 km | 7 | 42 | NW Outer ↔ SE Mid |
| line-2 | 12.0 km | 4 | 26 | NW Mid ↔ S Mid |
| line-3 | 11.2 km | 4 | 24 | S Mid ↔ E Inner |
| **Total** | **43.7 km** | **15 unique** | **92** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 20,331 train-km/day |
| Annual traction demand | 96.2 GWh |
| Station/depot PV / storage | 9.2 MW / 47.0 MWh |
| Aggregate charging power | 7.5 MW |
| Dedicated solar plant | 39.9 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 6.9 km / 56 kWh |
| Lowest traversal charging margin | line-3: 31 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $302 M |
| Stations | $68 M |
| Depots | $8.0 M |
| Rolling stock | $83 M |
| Dedicated solar plant | $32 M |
| Residual train control | $2.2 M |
| Charging microgrids | $1.6 M |
| EPC / project services | $33 M |
| **Total city programme** | **$530 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $111 M (21.0%) |
| Domestic / local capital | $419 M (79.0%) |
| Annual public construction commitment | $72 M / yr for 7 years |
| Annual post-grace debt service | $62 M / yr |
| External capital saved vs default turnkey sensitivity | $842 M |
| Capital + lifetime external interest saved | $1.90 bn |
| Annual OPEX | $12 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 184 assets / 875 tasks | [`sukkur-operations-manifest.json`](operations/sukkur-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`sukkur.toml`](sukkur.toml) | Expanded simulator scenario |
| [`sukkur.corridor.geojson`](sukkur.corridor.geojson) | GIS corridor and stations |
| [`sukkur.design-quality.yaml`](sukkur.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh sukkur
```
