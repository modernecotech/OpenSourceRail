# Beni-Mellal — Urban Rail Network

**Country:** MA · **Population:** 300,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Beni-Mellal-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$383 M (87.9%) of external capital** and **$471 M of external interest**. Capital plus saved interest totals **$855 M**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Beni-Mellal rail network on OpenStreetMap](beni-mellal-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 14 / 1 |
| Route length | 30.2 km double track |
| Coverage / transfer reachability | 84.8% / 100% |
| Estimated station catchment | 254,400 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 66 × 2-car `tram-2car` trainsets (59 peak revenue) |
| Peak network throughput | 28,800 passengers/hour |
| Practical service capacity | 267,840 passenger-trips/day |
| Annual paid-trip planning range | 48.9–78.2 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 |  9.4 km | 5 | 20 | NE Mid ↔ SW Outer |
| line-2 | 11.7 km | 5 | 26 | SW Mid ↔ NE Outer |
| line-3 |  9.1 km | 4 | 20 | S Mid ↔ N Outer |
| **Total** | **30.2 km** | **14 unique** | **66** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 14,050 train-km/day |
| Annual traction demand | 44.3 GWh |
| Station/depot PV / storage | 8.6 MW / 46.0 MWh |
| Aggregate charging power | 6.5 MW |
| Dedicated solar plant | 15.5 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 7.0 km / 34 kWh |
| Lowest traversal charging margin | line-3: 42 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $91 M |
| Stations | $76 M |
| Depots | $8.0 M |
| Rolling stock | $37 M |
| Dedicated solar plant | $12 M |
| Residual train control | $1.5 M |
| Charging microgrids | $1.5 M |
| EPC / project services | $15 M |
| **Total city programme** | **$242 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $53 M (21.9%) |
| Domestic / local capital | $189 M (78.1%) |
| Annual public construction commitment | $17 M / yr for 5 years |
| Annual post-grace debt service | $12 M / yr |
| External capital saved vs default turnkey sensitivity | $383 M |
| Capital + lifetime external interest saved | $855 M |
| Annual OPEX | $6.9 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 149 assets / 672 tasks | [`beni-mellal-operations-manifest.json`](operations/beni-mellal-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`beni-mellal.toml`](beni-mellal.toml) | Expanded simulator scenario |
| [`beni-mellal.corridor.geojson`](beni-mellal.corridor.geojson) | GIS corridor and stations |
| [`beni-mellal.design-quality.yaml`](beni-mellal.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh beni-mellal
```
