# Gazipur — Urban Rail Network

**Country:** BD · **Population:** 1,400,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Gazipur-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$3.61 bn (86.6%) of external capital** and **$4.53 bn of external interest**. Capital plus saved interest totals **$8.14 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Gazipur rail network on OpenStreetMap](gazipur-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 6 / 89 / 15 |
| Route length | 264.5 km double track |
| Coverage / transfer reachability | 46.3% / 47% |
| Estimated station catchment | 648,200 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 338 × 4-car `metro-4car` trainsets (305 peak revenue) |
| Peak network throughput | 115,200 passengers/hour |
| Practical service capacity | 982,080 passenger-trips/day |
| Annual paid-trip planning range | 179.2–286.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 37.5 km | 14 | 60 | S Mid ↔ N Mid |
| line-2 | 35.2 km | 12 | 52 | NW Mid ↔ E Outer |
| line-3 | 48.5 km | 16 | 75 | NE Outer ↔ SW Outer |
| line-4 | 47.0 km | 16 | 75 | SE Outer ↔ NW Outer |
| line-5 | 30.3 km | 10 | 49 | N Outer ↔ S Mid |
| line-6 | 66.1 km | 21 | 27 | NW Mid ↔ W Mid |
| **Total** | **264.5 km** | **89 unique** | **338** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,558 one-way journeys / 107,639 train-km/day |
| Annual traction demand | 678.9 GWh |
| Station/depot PV / storage | 28.7 MW / 158.5 MWh |
| Aggregate charging power | 120.0 MW |
| Dedicated solar plant | 412.6 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 10.9 km / 109 kWh |
| Lowest traversal charging margin | line-2: 201 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $920 M |
| Stations | $513 M |
| Depots | $8.0 M |
| Rolling stock | $379 M |
| Dedicated solar plant | $330 M |
| Residual train control | $13 M |
| Charging microgrids | $27 M |
| EPC / project services | $130 M |
| **Total city programme** | **$2.32 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $560 M (24.2%) |
| Domestic / local capital | $1.76 bn (75.8%) |
| Annual public construction commitment | $195 M / yr for 7 years |
| Annual post-grace debt service | $161 M / yr |
| External capital saved vs default turnkey sensitivity | $3.61 bn |
| Capital + lifetime external interest saved | $8.14 bn |
| Annual OPEX | $53 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 840 assets / 3,720 tasks | [`gazipur-operations-manifest.json`](operations/gazipur-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`gazipur.toml`](gazipur.toml) | Expanded simulator scenario |
| [`gazipur.corridor.geojson`](gazipur.corridor.geojson) | GIS corridor and stations |
| [`gazipur.design-quality.yaml`](gazipur.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
scripts/regenerate-city.sh gazipur
```
