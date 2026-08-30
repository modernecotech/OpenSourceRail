# Bukavu — Urban Rail Network

**Country:** CD · **Population:** 1,000,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Bukavu-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$736 M (86.0%) of external capital** and **$950 M of external interest**. Capital plus saved interest totals **$1.69 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Bukavu rail network on OpenStreetMap](bukavu-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 23 / 1 |
| Route length | 61.4 km double track |
| Coverage / transfer reachability | 55.8% / 100% |
| Estimated station catchment | 558,000 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 130 × 3-car `light-metro-3car` trainsets (117 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 18.3 km | 7 | 40 | NE Mid ↔ SW Mid |
| line-2 | 23.6 km | 9 | 49 | NW Outer ↔ SE Outer |
| line-3 | 19.4 km | 7 | 41 | SW Mid ↔ NE Outer |
| **Total** | **61.4 km** | **23 unique** | **130** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 28,540 train-km/day |
| Annual traction demand | 135.0 GWh |
| Station/depot PV / storage | 11.3 MW / 50.5 MWh |
| Aggregate charging power | 11.0 MW |
| Dedicated solar plant | 75.6 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 7.6 km / 57 kWh |
| Lowest traversal charging margin | line-2: 67 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $169 M |
| Stations | $89 M |
| Depots | $8.0 M |
| Rolling stock | $117 M |
| Dedicated solar plant | $60 M |
| Residual train control | $3.1 M |
| Charging microgrids | $2.4 M |
| EPC / project services | $27 M |
| **Total city programme** | **$475 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $120 M (25.2%) |
| Domestic / local capital | $355 M (74.8%) |
| Annual public construction commitment | $49 M / yr for 10 years |
| Annual post-grace debt service | $45 M / yr |
| External capital saved vs default turnkey sensitivity | $736 M |
| Capital + lifetime external interest saved | $1.69 bn |
| Annual OPEX | $12 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 267 assets / 1,264 tasks | [`bukavu-operations-manifest.json`](operations/bukavu-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`bukavu.toml`](bukavu.toml) | Expanded simulator scenario |
| [`bukavu.corridor.geojson`](bukavu.corridor.geojson) | GIS corridor and stations |
| [`bukavu.design-quality.yaml`](bukavu.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh bukavu
```
