# Hurghada — Urban Rail Network

**Country:** EG · **Population:** 300,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Hurghada-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$553 M (88.3%) of external capital** and **$679 M of external interest**. Capital plus saved interest totals **$1.23 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Hurghada rail network on OpenStreetMap](hurghada-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 17 / 3 |
| Route length | 39.0 km double track |
| Coverage / transfer reachability | 57.7% / 100% |
| Estimated station catchment | 173,100 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 80 × 2-car `tram-2car` trainsets (72 peak revenue) |
| Peak network throughput | 28,800 passengers/hour |
| Practical service capacity | 267,840 passenger-trips/day |
| Annual paid-trip planning range | 48.9–78.2 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 14.5 km | 6 | 30 | NW Outer ↔ SE Mid |
| line-2 | 15.2 km | 6 | 30 | S Outer ↔ NW Outer |
| line-3 |  9.3 km | 5 | 20 | E Mid ↔ S Mid |
| **Total** | **39.0 km** | **17 unique** | **80** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 18,120 train-km/day |
| Annual traction demand | 57.1 GWh |
| Station/depot PV / storage | 9.8 MW / 48.0 MWh |
| Aggregate charging power | 8.5 MW |
| Dedicated solar plant | 18.7 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 3.5 km / 19 kWh |
| Lowest traversal charging margin | line-3: 43 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $138 M |
| Stations | $116 M |
| Depots | $8.0 M |
| Rolling stock | $45 M |
| Dedicated solar plant | $15 M |
| Residual train control | $1.9 M |
| Charging microgrids | $2.0 M |
| EPC / project services | $22 M |
| **Total city programme** | **$348 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $73 M (21.1%) |
| Domestic / local capital | $274 M (78.9%) |
| Annual public construction commitment | $37 M / yr for 5 years |
| Annual post-grace debt service | $28 M / yr |
| External capital saved vs default turnkey sensitivity | $553 M |
| Capital + lifetime external interest saved | $1.23 bn |
| Annual OPEX | $8.6 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 183 assets / 822 tasks | [`hurghada-operations-manifest.json`](operations/hurghada-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`hurghada.toml`](hurghada.toml) | Expanded simulator scenario |
| [`hurghada.corridor.geojson`](hurghada.corridor.geojson) | GIS corridor and stations |
| [`hurghada.design-quality.yaml`](hurghada.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
scripts/regenerate-city.sh hurghada
```
