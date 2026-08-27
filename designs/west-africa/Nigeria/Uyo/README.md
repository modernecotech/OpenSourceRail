# Uyo — Urban Rail Network

**Country:** NG · **Population:** 800,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Uyo-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$492 M (86.6%) of external capital** and **$617 M of external interest**. Capital plus saved interest totals **$1.11 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Uyo rail network on OpenStreetMap](uyo-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 14 / 2 |
| Route length | 34.0 km double track |
| Coverage / transfer reachability | 69.7% / 100% |
| Estimated station catchment | 557,600 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 76 × 3-car `light-metro-3car` trainsets (67 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 16.2 km | 6 | 35 | SW Mid ↔ E Outer |
| line-2 |  9.5 km | 5 | 23 | NW Mid ↔ SE Inner |
| line-3 |  8.4 km | 3 | 18 | NE Inner ↔ SW Mid |
| **Total** | **34.0 km** | **14 unique** | **76** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 15,823 train-km/day |
| Annual traction demand | 74.9 GWh |
| Station/depot PV / storage | 8.9 MW / 46.5 MWh |
| Aggregate charging power | 7.0 MW |
| Dedicated solar plant | 38.9 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 6.5 km / 49 kWh |
| Lowest traversal charging margin | line-3: 29 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $110 M |
| Stations | $76 M |
| Depots | $8.0 M |
| Rolling stock | $68 M |
| Dedicated solar plant | $31 M |
| Residual train control | $1.7 M |
| Charging microgrids | $1.6 M |
| EPC / project services | $19 M |
| **Total city programme** | **$316 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $76 M (24.1%) |
| Domestic / local capital | $240 M (75.9%) |
| Annual public construction commitment | $36 M / yr for 7 years |
| Annual post-grace debt service | $31 M / yr |
| External capital saved vs default turnkey sensitivity | $492 M |
| Capital + lifetime external interest saved | $1.11 bn |
| Annual OPEX | $7.9 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 163 assets / 748 tasks | [`uyo-operations-manifest.json`](operations/uyo-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`uyo.toml`](uyo.toml) | Expanded simulator scenario |
| [`uyo.corridor.geojson`](uyo.corridor.geojson) | GIS corridor and stations |
| [`uyo.design-quality.yaml`](uyo.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
scripts/regenerate-city.sh uyo
```
