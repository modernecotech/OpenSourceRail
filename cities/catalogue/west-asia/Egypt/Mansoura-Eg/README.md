# Mansoura-Eg — Urban Rail Network

**Country:** EG · **Population:** 1,000,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Mansoura-Eg-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$657 M (86.6%) of external capital** and **$807 M of external interest**. Capital plus saved interest totals **$1.46 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Mansoura-Eg rail network on OpenStreetMap](mansoura-eg-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 19 / 1 |
| Route length | 51.6 km double track |
| Coverage / transfer reachability | 70.8% / 100% |
| Estimated station catchment | 708,000 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 109 × 3-car `light-metro-3car` trainsets (98 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 13.2 km | 5 | 29 | SE Inner ↔ N Mid |
| line-2 | 13.2 km | 6 | 28 | NE Mid ↔ W Mid |
| line-3 | 25.3 km | 8 | 52 | NE Mid ↔ SW Outer |
| **Total** | **51.6 km** | **19 unique** | **109** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 24,012 train-km/day |
| Annual traction demand | 113.6 GWh |
| Station/depot PV / storage | 10.1 MW / 48.5 MWh |
| Aggregate charging power | 9.0 MW |
| Dedicated solar plant | 48.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 12.0 km / 97 kWh |
| Lowest traversal charging margin | line-2: 30 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $152 M |
| Stations | $95 M |
| Depots | $8.0 M |
| Rolling stock | $98 M |
| Dedicated solar plant | $38 M |
| Residual train control | $2.6 M |
| Charging microgrids | $2.0 M |
| EPC / project services | $25 M |
| **Total city programme** | **$421 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $101 M (24.0%) |
| Domestic / local capital | $320 M (76.0%) |
| Annual public construction commitment | $44 M / yr for 5 years |
| Annual post-grace debt service | $34 M / yr |
| External capital saved vs default turnkey sensitivity | $657 M |
| Capital + lifetime external interest saved | $1.46 bn |
| Annual OPEX | $11 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 224 assets / 1,055 tasks | [`mansoura-eg-operations-manifest.json`](operations/mansoura-eg-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`mansoura-eg.toml`](mansoura-eg.toml) | Expanded simulator scenario |
| [`mansoura-eg.corridor.geojson`](mansoura-eg.corridor.geojson) | GIS corridor and stations |
| [`mansoura-eg.design-quality.yaml`](mansoura-eg.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh mansoura-eg
```
