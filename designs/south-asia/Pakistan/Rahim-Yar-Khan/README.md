# Rahim-Yar-Khan — Urban Rail Network

**Country:** PK · **Population:** 500,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Rahim-Yar-Khan-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$685 M (86.3%) of external capital** and **$859 M of external interest**. Capital plus saved interest totals **$1.54 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Rahim-Yar-Khan rail network on OpenStreetMap](rahim-yar-khan-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 18 / 2 |
| Route length | 53.6 km double track |
| Coverage / transfer reachability | 75.8% / 100% |
| Estimated station catchment | 379,000 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 129 × 3-car `light-metro-3car` trainsets (116 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 10.2 km | 6 | 30 | NW Inner ↔ SE Mid |
| line-2 | 18.4 km | 5 | 42 | SW Mid ↔ NE Outer |
| line-3 | 25.1 km | 7 | 57 | NE Outer ↔ SW Outer |
| **Total** | **53.6 km** | **18 unique** | **129** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 24,913 train-km/day |
| Annual traction demand | 117.8 GWh |
| Station/depot PV / storage | 9.2 MW / 54.0 MWh |
| Aggregate charging power | 15.0 MW |
| Dedicated solar plant | 51.3 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 13.0 km / 105 kWh |
| Lowest traversal charging margin | line-2: 66 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $161 M |
| Stations | $82 M |
| Depots | $8.0 M |
| Rolling stock | $116 M |
| Dedicated solar plant | $41 M |
| Residual train control | $2.7 M |
| Charging microgrids | $3.5 M |
| EPC / project services | $26 M |
| **Total city programme** | **$441 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $108 M (24.6%) |
| Domestic / local capital | $332 M (75.4%) |
| Annual public construction commitment | $58 M / yr for 7 years |
| Annual post-grace debt service | $51 M / yr |
| External capital saved vs default turnkey sensitivity | $685 M |
| Capital + lifetime external interest saved | $1.54 bn |
| Annual OPEX | $11 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 241 assets / 1,178 tasks | [`rahim-yar-khan-operations-manifest.json`](operations/rahim-yar-khan-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`rahim-yar-khan.toml`](rahim-yar-khan.toml) | Expanded simulator scenario |
| [`rahim-yar-khan.corridor.geojson`](rahim-yar-khan.corridor.geojson) | GIS corridor and stations |
| [`rahim-yar-khan.design-quality.yaml`](rahim-yar-khan.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
scripts/regenerate-city.sh rahim-yar-khan
```
