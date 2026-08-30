# Ibb — Urban Rail Network

**Country:** YE · **Population:** 750,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Ibb-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$639 M (86.7%) of external capital** and **$825 M of external interest**. Capital plus saved interest totals **$1.46 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Ibb rail network on OpenStreetMap](ibb-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 18 / 2 |
| Route length | 49.9 km double track |
| Coverage / transfer reachability | 74.1% / 100% |
| Estimated station catchment | 555,750 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 106 × 3-car `light-metro-3car` trainsets (95 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 14.6 km | 6 | 31 | NE Inner ↔ SW Mid |
| line-2 | 21.6 km | 7 | 46 | S Mid ↔ NW Outer |
| line-3 | 13.6 km | 5 | 29 | S Mid ↔ NE Mid |
| **Total** | **49.9 km** | **18 unique** | **106** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 23,202 train-km/day |
| Annual traction demand | 109.8 GWh |
| Station/depot PV / storage | 9.8 MW / 48.0 MWh |
| Aggregate charging power | 8.5 MW |
| Dedicated solar plant | 44.5 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 9.1 km / 66 kWh |
| Lowest traversal charging margin | line-3: 55 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $146 M |
| Stations | $95 M |
| Depots | $8.0 M |
| Rolling stock | $95 M |
| Dedicated solar plant | $36 M |
| Residual train control | $2.5 M |
| Charging microgrids | $1.9 M |
| EPC / project services | $24 M |
| **Total city programme** | **$409 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $98 M (24.0%) |
| Domestic / local capital | $311 M (76.0%) |
| Annual public construction commitment | $55 M / yr for 10 years |
| Annual post-grace debt service | $51 M / yr |
| External capital saved vs default turnkey sensitivity | $639 M |
| Capital + lifetime external interest saved | $1.46 bn |
| Annual OPEX | $9.9 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 215 assets / 1,018 tasks | [`ibb-operations-manifest.json`](operations/ibb-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`ibb.toml`](ibb.toml) | Expanded simulator scenario |
| [`ibb.corridor.geojson`](ibb.corridor.geojson) | GIS corridor and stations |
| [`ibb.design-quality.yaml`](ibb.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh ibb
```
