# Kabul — Urban Rail Network

**Country:** AF · **Population:** 4,601,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Kabul-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$3.60 bn (85.7%) of external capital** and **$4.65 bn of external interest**. Capital plus saved interest totals **$8.24 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Kabul rail network on OpenStreetMap](kabul-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 7 / 80 / 11 |
| Route length | 228.8 km double track |
| Coverage / transfer reachability | 59.0% / 38% |
| Estimated station catchment | 2,714,590 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 350 × 6-car `metro-6car` trainsets (316 peak revenue) |
| Peak network throughput | 201,600 passengers/hour |
| Practical service capacity | 1,740,960 passenger-trips/day |
| Annual paid-trip planning range | 317.7–508.4 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 29.6 km | 13 | 60 | NE Outer ↔ SW Mid |
| line-2 | 33.7 km | 12 | 65 | SE Mid ↔ NW Outer |
| line-3 | 23.0 km | 9 | 43 | W Mid ↔ NE Mid |
| line-4 | 29.8 km | 11 | 54 | SW Outer ↔ E Outer |
| line-5 | 30.8 km | 10 | 59 | NW Mid ↔ E Outer |
| line-6 | 20.8 km | 7 | 41 | SE Outer ↔ N Inner |
| line-7 | 61.1 km | 18 | 28 | NW Mid ↔ W Mid |
| **Total** | **228.8 km** | **80 unique** | **350** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 3,022 one-way journeys / 92,179 train-km/day |
| Annual traction demand | 872.1 GWh |
| Station/depot PV / storage | 28.1 MW / 194.0 MWh |
| Aggregate charging power | 156.0 MW |
| Dedicated solar plant | 410.9 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 7.8 km / 113 kWh |
| Lowest traversal charging margin | line-6: 275 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $793 M |
| Stations | $438 M |
| Depots | $8.0 M |
| Rolling stock | $588 M |
| Dedicated solar plant | $329 M |
| Residual train control | $11 M |
| Charging microgrids | $34 M |
| EPC / project services | $131 M |
| **Total city programme** | **$2.33 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $601 M (25.8%) |
| Domestic / local capital | $1.73 bn (74.2%) |
| Annual public construction commitment | $311 M / yr for 10 years |
| Annual post-grace debt service | $288 M / yr |
| External capital saved vs default turnkey sensitivity | $3.60 bn |
| Capital + lifetime external interest saved | $8.24 bn |
| Annual OPEX | $55 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 813 assets / 3,686 tasks | [`kabul-operations-manifest.json`](operations/kabul-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`kabul.toml`](kabul.toml) | Expanded simulator scenario |
| [`kabul.corridor.geojson`](kabul.corridor.geojson) | GIS corridor and stations |
| [`kabul.design-quality.yaml`](kabul.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
scripts/regenerate-city.sh kabul
```
