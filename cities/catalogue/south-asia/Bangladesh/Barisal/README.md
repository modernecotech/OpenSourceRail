# Barisal — Urban Rail Network

**Country:** BD · **Population:** 550,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Barisal-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$834 M (86.6%) of external capital** and **$1.04 bn of external interest**. Capital plus saved interest totals **$1.88 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Barisal rail network on OpenStreetMap](barisal-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 23 / 1 |
| Route length | 61.2 km double track |
| Coverage / transfer reachability | 56.5% / 100% |
| Estimated station catchment | 310,749 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 130 × 3-car `light-metro-3car` trainsets (117 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 15.3 km | 8 | 35 | NW Mid ↔ S Mid |
| line-2 | 20.3 km | 7 | 41 | NE Mid ↔ S Outer |
| line-3 | 25.6 km | 8 | 54 | NW Outer ↔ SE Mid |
| **Total** | **61.2 km** | **23 unique** | **130** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 28,473 train-km/day |
| Annual traction demand | 134.7 GWh |
| Station/depot PV / storage | 11.0 MW / 50.0 MWh |
| Aggregate charging power | 10.5 MW |
| Dedicated solar plant | 75.8 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 10.5 km / 79 kWh |
| Lowest traversal charging margin | line-2: 61 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $222 M |
| Stations | $91 M |
| Depots | $8.0 M |
| Rolling stock | $117 M |
| Dedicated solar plant | $61 M |
| Residual train control | $3.1 M |
| Charging microgrids | $2.2 M |
| EPC / project services | $31 M |
| **Total city programme** | **$535 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $129 M (24.1%) |
| Domestic / local capital | $406 M (75.9%) |
| Annual public construction commitment | $45 M / yr for 7 years |
| Annual post-grace debt service | $37 M / yr |
| External capital saved vs default turnkey sensitivity | $834 M |
| Capital + lifetime external interest saved | $1.88 bn |
| Annual OPEX | $13 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 266 assets / 1,261 tasks | [`barisal-operations-manifest.json`](operations/barisal-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`barisal.toml`](barisal.toml) | Expanded simulator scenario |
| [`barisal.corridor.geojson`](barisal.corridor.geojson) | GIS corridor and stations |
| [`barisal.design-quality.yaml`](barisal.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh barisal
```
