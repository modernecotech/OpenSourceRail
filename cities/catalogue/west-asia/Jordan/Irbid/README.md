# Irbid — Urban Rail Network

**Country:** JO · **Population:** 600,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Irbid-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$591 M (86.2%) of external capital** and **$726 M of external interest**. Capital plus saved interest totals **$1.32 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Irbid rail network on OpenStreetMap](irbid-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 21 / 1 |
| Route length | 48.7 km double track |
| Coverage / transfer reachability | 65.1% / 100% |
| Estimated station catchment | 390,600 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 107 × 3-car `light-metro-3car` trainsets (96 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 15.8 km | 7 | 36 | S Mid ↔ N Outer |
| line-2 | 14.0 km | 7 | 31 | E Outer ↔ W Mid |
| line-3 | 18.9 km | 7 | 40 | NE Outer ↔ SW Outer |
| **Total** | **48.7 km** | **21 unique** | **107** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 22,637 train-km/day |
| Annual traction demand | 107.1 GWh |
| Station/depot PV / storage | 11.0 MW / 50.0 MWh |
| Aggregate charging power | 10.5 MW |
| Dedicated solar plant | 48.7 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 4.9 km / 35 kWh |
| Lowest traversal charging margin | line-2: 61 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $127 M |
| Stations | $84 M |
| Depots | $8.0 M |
| Rolling stock | $96 M |
| Dedicated solar plant | $39 M |
| Residual train control | $2.4 M |
| Charging microgrids | $2.2 M |
| EPC / project services | $22 M |
| **Total city programme** | **$381 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $94 M (24.8%) |
| Domestic / local capital | $286 M (75.2%) |
| Annual public construction commitment | $33 M / yr for 5 years |
| Annual post-grace debt service | $24 M / yr |
| External capital saved vs default turnkey sensitivity | $591 M |
| Capital + lifetime external interest saved | $1.32 bn |
| Annual OPEX | $12 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 232 assets / 1,073 tasks | [`irbid-operations-manifest.json`](operations/irbid-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`irbid.toml`](irbid.toml) | Expanded simulator scenario |
| [`irbid.corridor.geojson`](irbid.corridor.geojson) | GIS corridor and stations |
| [`irbid.design-quality.yaml`](irbid.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh irbid
```
