# Kano — Urban Rail Network

**Country:** NG · **Population:** 4,200,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Kano-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$6.81 bn (85.7%) of external capital** and **$8.53 bn of external interest**. Capital plus saved interest totals **$15.34 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Kano rail network on OpenStreetMap](kano-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 9 / 142 / 16 |
| Route length | 434.4 km double track |
| Coverage / transfer reachability | 57.8% / 61% |
| Estimated station catchment | 2,427,600 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 686 × 6-car `metro-6car` trainsets (619 peak revenue) |
| Peak network throughput | 259,200 passengers/hour |
| Practical service capacity | 2,276,640 passenger-trips/day |
| Annual paid-trip planning range | 415.5–664.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 43.4 km | 15 | 76 | W Mid ↔ E Mid |
| line-2 | 46.0 km | 17 | 90 | SE Outer ↔ NW Mid |
| line-3 | 45.1 km | 15 | 83 | SW Outer ↔ NE Mid |
| line-4 | 39.3 km | 14 | 76 | SE Outer ↔ NW Mid |
| line-5 | 38.3 km | 13 | 71 | NE Outer ↔ SW Inner |
| line-6 | 33.9 km | 10 | 61 | N Inner ↔ S Mid |
| line-7 | 52.6 km | 17 | 100 | NE Outer ↔ S Mid |
| line-8 | 45.9 km | 15 | 89 | SE Inner ↔ NW Outer |
| line-9 | 90.0 km | 26 | 40 | NW Mid ↔ NW Mid |
| **Total** | **434.4 km** | **142 unique** | **686** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 3,952 one-way journeys / 181,087 train-km/day |
| Annual traction demand | 1,713.2 GWh |
| Station/depot PV / storage | 42.8 MW / 292.0 MWh |
| Aggregate charging power | 254.0 MW |
| Dedicated solar plant | 781.2 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-8: 18.6 km / 311 kWh |
| Lowest traversal charging margin | line-6: 227 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.58 bn |
| Stations | $726 M |
| Depots | $8.0 M |
| Rolling stock | $1.15 bn |
| Dedicated solar plant | $625 M |
| Residual train control | $22 M |
| Charging microgrids | $55 M |
| EPC / project services | $248 M |
| **Total city programme** | **$4.41 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.14 bn (25.8%) |
| Domestic / local capital | $3.28 bn (74.2%) |
| Annual public construction commitment | $499 M / yr for 7 years |
| Annual post-grace debt service | $426 M / yr |
| External capital saved vs default turnkey sensitivity | $6.81 bn |
| Capital + lifetime external interest saved | $15.34 bn |
| Annual OPEX | $109 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 1,501 assets / 6,978 tasks | [`kano-operations-manifest.json`](operations/kano-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`kano.toml`](kano.toml) | Expanded simulator scenario |
| [`kano.corridor.geojson`](kano.corridor.geojson) | GIS corridor and stations |
| [`kano.design-quality.yaml`](kano.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh kano
```
