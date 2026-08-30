# Mwanza — Urban Rail Network

**Country:** TZ · **Population:** 1,100,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Mwanza-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$2.35 bn (86.5%) of external capital** and **$2.94 bn of external interest**. Capital plus saved interest totals **$5.29 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Mwanza rail network on OpenStreetMap](mwanza-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 6 / 62 / 8 |
| Route length | 175.9 km double track |
| Coverage / transfer reachability | 75.8% / 40% |
| Estimated station catchment | 833,800 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 219 × 4-car `metro-4car` trainsets (197 peak revenue) |
| Peak network throughput | 115,200 passengers/hour |
| Practical service capacity | 982,080 passenger-trips/day |
| Annual paid-trip planning range | 179.2–286.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 25.6 km | 10 | 42 | S Mid ↔ N Mid |
| line-2 | 23.0 km | 9 | 38 | W Mid ↔ E Mid |
| line-3 | 18.3 km | 7 | 29 | SW Mid ↔ NW Mid |
| line-4 | 26.0 km | 11 | 43 | NE Outer ↔ W Mid |
| line-5 | 29.9 km | 8 | 47 | NW Mid ↔ SE Outer |
| line-6 | 53.2 km | 17 | 20 | N Mid ↔ N Mid |
| **Total** | **175.9 km** | **62 unique** | **219** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,558 one-way journeys / 69,429 train-km/day |
| Annual traction demand | 437.9 GWh |
| Station/depot PV / storage | 22.4 MW / 127.0 MWh |
| Aggregate charging power | 88.5 MW |
| Dedicated solar plant | 261.7 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-5: 13.0 km / 130 kWh |
| Lowest traversal charging margin | line-3: 142 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $565 M |
| Stations | $366 M |
| Depots | $8.0 M |
| Rolling stock | $245 M |
| Dedicated solar plant | $209 M |
| Residual train control | $8.8 M |
| Charging microgrids | $20 M |
| EPC / project services | $85 M |
| **Total city programme** | **$1.51 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $365 M (24.2%) |
| Domestic / local capital | $1.14 bn (75.8%) |
| Annual public construction commitment | $136 M / yr for 7 years |
| Annual post-grace debt service | $113 M / yr |
| External capital saved vs default turnkey sensitivity | $2.35 bn |
| Capital + lifetime external interest saved | $5.29 bn |
| Annual OPEX | $35 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 568 assets / 2,476 tasks | [`mwanza-operations-manifest.json`](operations/mwanza-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`mwanza.toml`](mwanza.toml) | Expanded simulator scenario |
| [`mwanza.corridor.geojson`](mwanza.corridor.geojson) | GIS corridor and stations |
| [`mwanza.design-quality.yaml`](mwanza.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh mwanza
```
