# Aden — Urban Rail Network

**Country:** YE · **Population:** 985,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Aden-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$588 M (86.7%) of external capital** and **$759 M of external interest**. Capital plus saved interest totals **$1.35 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Aden rail network on OpenStreetMap](aden-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 17 / 1 |
| Route length | 45.8 km double track |
| Coverage / transfer reachability | 72.0% / 100% |
| Estimated station catchment | 709,200 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 97 × 3-car `light-metro-3car` trainsets (87 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 16.5 km | 6 | 36 | NW Outer ↔ S Mid |
| line-2 | 14.2 km | 5 | 30 | NE Mid ↔ SW Outer |
| line-3 | 15.1 km | 6 | 31 | N Outer ↔ SE Mid |
| **Total** | **45.8 km** | **17 unique** | **97** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 21,316 train-km/day |
| Annual traction demand | 100.8 GWh |
| Station/depot PV / storage | 9.8 MW / 48.0 MWh |
| Aggregate charging power | 8.5 MW |
| Dedicated solar plant | 41.7 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 7.0 km / 56 kWh |
| Lowest traversal charging margin | line-2: 37 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $134 M |
| Stations | $88 M |
| Depots | $8.0 M |
| Rolling stock | $87 M |
| Dedicated solar plant | $33 M |
| Residual train control | $2.3 M |
| Charging microgrids | $1.9 M |
| EPC / project services | $22 M |
| **Total city programme** | **$377 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $90 M (24.0%) |
| Domestic / local capital | $286 M (76.0%) |
| Annual public construction commitment | $51 M / yr for 10 years |
| Annual post-grace debt service | $47 M / yr |
| External capital saved vs default turnkey sensitivity | $588 M |
| Capital + lifetime external interest saved | $1.35 bn |
| Annual OPEX | $9.1 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 201 assets / 942 tasks | [`aden-operations-manifest.json`](operations/aden-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`aden.toml`](aden.toml) | Expanded simulator scenario |
| [`aden.corridor.geojson`](aden.corridor.geojson) | GIS corridor and stations |
| [`aden.design-quality.yaml`](aden.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
scripts/regenerate-city.sh aden
```
