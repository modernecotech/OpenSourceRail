# Mecca — Urban Rail Network

**Country:** SA · **Population:** 2,200,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Mecca-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$2.84 bn (87.0%) of external capital** and **$3.49 bn of external interest**. Capital plus saved interest totals **$6.33 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Mecca rail network on OpenStreetMap](mecca-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 6 / 77 / 12 |
| Route length | 223.1 km double track |
| Coverage / transfer reachability | 45.9% / 47% |
| Estimated station catchment | 1,009,800 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 271 × 4-car `metro-4car` trainsets (244 peak revenue) |
| Peak network throughput | 115,200 passengers/hour |
| Practical service capacity | 982,080 passenger-trips/day |
| Annual paid-trip planning range | 179.2–286.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 31.2 km | 13 | 52 | W Mid ↔ SE Outer |
| line-2 | 25.3 km | 9 | 40 | SE Outer ↔ W Mid |
| line-3 | 37.1 km | 13 | 60 | NE Outer ↔ SW Mid |
| line-4 | 33.9 km | 12 | 52 | N Mid ↔ S Outer |
| line-5 | 24.3 km | 8 | 39 | E Mid ↔ NW Outer |
| line-6 | 71.4 km | 22 | 28 | W Mid ↔ W Mid |
| **Total** | **223.1 km** | **77 unique** | **271** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,558 one-way journeys / 87,151 train-km/day |
| Annual traction demand | 549.7 GWh |
| Station/depot PV / storage | 25.4 MW / 142.0 MWh |
| Aggregate charging power | 103.5 MW |
| Dedicated solar plant | 259.4 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-6: 13.0 km / 140 kWh |
| Lowest traversal charging margin | line-5: 166 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $745 M |
| Stations | $411 M |
| Depots | $8.0 M |
| Rolling stock | $304 M |
| Dedicated solar plant | $208 M |
| Residual train control | $11 M |
| Charging microgrids | $23 M |
| EPC / project services | $105 M |
| **Total city programme** | **$1.81 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $426 M (23.5%) |
| Domestic / local capital | $1.39 bn (76.5%) |
| Annual public construction commitment | $125 M / yr for 5 years |
| Annual post-grace debt service | $88 M / yr |
| External capital saved vs default turnkey sensitivity | $2.84 bn |
| Capital + lifetime external interest saved | $6.33 bn |
| Annual OPEX | $67 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 702 assets / 3,062 tasks | [`mecca-operations-manifest.json`](operations/mecca-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`mecca.toml`](mecca.toml) | Expanded simulator scenario |
| [`mecca.corridor.geojson`](mecca.corridor.geojson) | GIS corridor and stations |
| [`mecca.design-quality.yaml`](mecca.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
scripts/regenerate-city.sh mecca
```
