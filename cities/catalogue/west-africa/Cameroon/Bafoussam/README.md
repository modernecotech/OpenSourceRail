# Bafoussam — Urban Rail Network

**Country:** CM · **Population:** 600,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Bafoussam-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$844 M (85.8%) of external capital** and **$1.06 bn of external interest**. Capital plus saved interest totals **$1.90 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Bafoussam rail network on OpenStreetMap](bafoussam-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 27 / 1 |
| Route length | 73.5 km double track |
| Coverage / transfer reachability | 47.1% / 100% |
| Estimated station catchment | 282,600 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 158 × 3-car `light-metro-3car` trainsets (142 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 23.0 km | 9 | 49 | N Mid ↔ S Outer |
| line-2 | 24.0 km | 9 | 52 | NW Outer ↔ E Mid |
| line-3 | 26.4 km | 9 | 57 | E Mid ↔ SW Outer |
| **Total** | **73.5 km** | **27 unique** | **158** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 34,183 train-km/day |
| Annual traction demand | 161.7 GWh |
| Station/depot PV / storage | 11.6 MW / 51.0 MWh |
| Aggregate charging power | 11.5 MW |
| Dedicated solar plant | 92.8 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 12.9 km / 97 kWh |
| Lowest traversal charging margin | line-1: 72 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $194 M |
| Stations | $91 M |
| Depots | $8.0 M |
| Rolling stock | $142 M |
| Dedicated solar plant | $74 M |
| Residual train control | $3.7 M |
| Charging microgrids | $2.5 M |
| EPC / project services | $31 M |
| **Total city programme** | **$547 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $140 M (25.6%) |
| Domestic / local capital | $407 M (74.4%) |
| Annual public construction commitment | $46 M / yr for 7 years |
| Annual post-grace debt service | $38 M / yr |
| External capital saved vs default turnkey sensitivity | $844 M |
| Capital + lifetime external interest saved | $1.90 bn |
| Annual OPEX | $14 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 316 assets / 1,515 tasks | [`bafoussam-operations-manifest.json`](operations/bafoussam-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`bafoussam.toml`](bafoussam.toml) | Expanded simulator scenario |
| [`bafoussam.corridor.geojson`](bafoussam.corridor.geojson) | GIS corridor and stations |
| [`bafoussam.design-quality.yaml`](bafoussam.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh bafoussam
```
