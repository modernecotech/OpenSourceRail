# Khartoum — Urban Rail Network

**Country:** SD · **Population:** 5,829,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Khartoum-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$6.32 bn (85.4%) of external capital** and **$8.16 bn of external interest**. Capital plus saved interest totals **$14.48 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Khartoum rail network on OpenStreetMap](khartoum-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 9 / 137 / 18 |
| Route length | 417.0 km double track |
| Coverage / transfer reachability | 57.9% / 44% |
| Estimated station catchment | 3,374,990 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 637 × 6-car `metro-6car` trainsets (574 peak revenue) |
| Peak network throughput | 259,200 passengers/hour |
| Practical service capacity | 2,276,640 passenger-trips/day |
| Annual paid-trip planning range | 415.5–664.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 40.8 km | 13 | 76 | SE Mid ↔ NW Mid |
| line-2 | 35.6 km | 14 | 68 | E Mid ↔ W Mid |
| line-3 | 56.0 km | 17 | 102 | NW Mid ↔ SE Outer |
| line-4 | 31.7 km | 12 | 59 | NW Mid ↔ S Mid |
| line-5 | 41.7 km | 14 | 79 | N Mid ↔ SW Mid |
| line-6 | 34.2 km | 11 | 63 | S Mid ↔ NE Mid |
| line-7 | 40.7 km | 13 | 74 | W Outer ↔ SE Mid |
| line-8 | 36.6 km | 13 | 71 | SW Mid ↔ N Outer |
| line-9 | 99.9 km | 30 | 45 | NW Mid ↔ NW Mid |
| **Total** | **417.0 km** | **137 unique** | **637** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 3,952 one-way journeys / 170,707 train-km/day |
| Annual traction demand | 1,615.0 GWh |
| Station/depot PV / storage | 42.5 MW / 290.0 MWh |
| Aggregate charging power | 252.0 MW |
| Dedicated solar plant | 799.2 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 14.4 km / 232 kWh |
| Lowest traversal charging margin | line-6: 243 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.37 bn |
| Stations | $723 M |
| Depots | $8.0 M |
| Rolling stock | $1.07 bn |
| Dedicated solar plant | $639 M |
| Residual train control | $21 M |
| Charging microgrids | $55 M |
| EPC / project services | $227 M |
| **Total city programme** | **$4.11 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.08 bn (26.3%) |
| Domestic / local capital | $3.03 bn (73.7%) |
| Annual public construction commitment | $473 M / yr for 10 years |
| Annual post-grace debt service | $435 M / yr |
| External capital saved vs default turnkey sensitivity | $6.32 bn |
| Capital + lifetime external interest saved | $14.48 bn |
| Annual OPEX | $99 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 1,426 assets / 6,567 tasks | [`khartoum-operations-manifest.json`](operations/khartoum-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`khartoum.toml`](khartoum.toml) | Expanded simulator scenario |
| [`khartoum.corridor.geojson`](khartoum.corridor.geojson) | GIS corridor and stations |
| [`khartoum.design-quality.yaml`](khartoum.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
scripts/regenerate-city.sh khartoum
```
