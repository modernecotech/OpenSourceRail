# La-Paz — Urban Rail Network

**Country:** BO · **Population:** 1,815,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only La-Paz-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$3.16 bn (86.8%) of external capital** and **$3.89 bn of external interest**. Capital plus saved interest totals **$7.05 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![La-Paz rail network on OpenStreetMap](la-paz-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 6 / 79 / 12 |
| Route length | 223.9 km double track |
| Coverage / transfer reachability | 60.7% / 53% |
| Estimated station catchment | 1,101,705 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 285 × 4-car `metro-4car` trainsets (256 peak revenue) |
| Peak network throughput | 115,200 passengers/hour |
| Practical service capacity | 982,080 passenger-trips/day |
| Annual paid-trip planning range | 179.2–286.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 33.7 km | 12 | 56 | NE Outer ↔ SW Mid |
| line-2 | 37.2 km | 13 | 58 | W Outer ↔ E Outer |
| line-3 | 30.0 km | 10 | 49 | NE Mid ↔ SW Outer |
| line-4 | 33.3 km | 12 | 54 | SE Outer ↔ NW Mid |
| line-5 | 27.6 km | 10 | 43 | S Mid ↔ N Mid |
| line-6 | 62.0 km | 22 | 25 | W Mid ↔ W Mid |
| **Total** | **223.9 km** | **79 unique** | **285** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,558 one-way journeys / 89,697 train-km/day |
| Annual traction demand | 565.7 GWh |
| Station/depot PV / storage | 26.9 MW / 149.5 MWh |
| Aggregate charging power | 111.0 MW |
| Dedicated solar plant | 325.6 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 12.8 km / 123 kWh |
| Lowest traversal charging margin | line-5: 248 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $814 M |
| Stations | $471 M |
| Depots | $8.0 M |
| Rolling stock | $319 M |
| Dedicated solar plant | $260 M |
| Residual train control | $11 M |
| Charging microgrids | $25 M |
| EPC / project services | $115 M |
| **Total city programme** | **$2.02 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $480 M (23.7%) |
| Domestic / local capital | $1.54 bn (76.3%) |
| Annual public construction commitment | $213 M / yr for 5 years |
| Annual post-grace debt service | $161 M / yr |
| External capital saved vs default turnkey sensitivity | $3.16 bn |
| Capital + lifetime external interest saved | $7.05 bn |
| Annual OPEX | $48 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 730 assets / 3,200 tasks | [`la-paz-operations-manifest.json`](operations/la-paz-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`la-paz.toml`](la-paz.toml) | Expanded simulator scenario |
| [`la-paz.corridor.geojson`](la-paz.corridor.geojson) | GIS corridor and stations |
| [`la-paz.design-quality.yaml`](la-paz.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
scripts/regenerate-city.sh la-paz
```
