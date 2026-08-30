# Sohag — Urban Rail Network

**Country:** EG · **Population:** 550,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Sohag-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$617 M (86.9%) of external capital** and **$758 M of external interest**. Capital plus saved interest totals **$1.38 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Sohag rail network on OpenStreetMap](sohag-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 17 / 1 |
| Route length | 44.4 km double track |
| Coverage / transfer reachability | 76.9% / 100% |
| Estimated station catchment | 422,950 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 98 × 3-car `light-metro-3car` trainsets (88 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 |  9.0 km | 4 | 20 | NE Mid ↔ NW Mid |
| line-2 | 16.7 km | 6 | 37 | N Inner ↔ SW Outer |
| line-3 | 18.7 km | 7 | 41 | N Inner ↔ SE Outer |
| **Total** | **44.4 km** | **17 unique** | **98** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 20,649 train-km/day |
| Annual traction demand | 97.7 GWh |
| Station/depot PV / storage | 8.9 MW / 46.5 MWh |
| Aggregate charging power | 7.0 MW |
| Dedicated solar plant | 41.1 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 13.0 km / 105 kWh |
| Lowest traversal charging margin | line-1: 34 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $151 M |
| Stations | $87 M |
| Depots | $8.0 M |
| Rolling stock | $88 M |
| Dedicated solar plant | $33 M |
| Residual train control | $2.2 M |
| Charging microgrids | $1.6 M |
| EPC / project services | $24 M |
| **Total city programme** | **$394 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $93 M (23.6%) |
| Domestic / local capital | $301 M (76.4%) |
| Annual public construction commitment | $42 M / yr for 5 years |
| Annual post-grace debt service | $31 M / yr |
| External capital saved vs default turnkey sensitivity | $617 M |
| Capital + lifetime external interest saved | $1.38 bn |
| Annual OPEX | $10 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 199 assets / 940 tasks | [`sohag-operations-manifest.json`](operations/sohag-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`sohag.toml`](sohag.toml) | Expanded simulator scenario |
| [`sohag.corridor.geojson`](sohag.corridor.geojson) | GIS corridor and stations |
| [`sohag.design-quality.yaml`](sohag.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh sohag
```
