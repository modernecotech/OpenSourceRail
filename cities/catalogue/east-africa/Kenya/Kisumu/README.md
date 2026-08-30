# Kisumu — Urban Rail Network

**Country:** KE · **Population:** 600,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Kisumu-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$668 M (86.1%) of external capital** and **$838 M of external interest**. Capital plus saved interest totals **$1.51 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Kisumu rail network on OpenStreetMap](kisumu-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 21 / 1 |
| Route length | 53.5 km double track |
| Coverage / transfer reachability | 69.3% / 100% |
| Estimated station catchment | 415,799 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 115 × 3-car `light-metro-3car` trainsets (103 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 17.1 km | 8 | 37 | SW Mid ↔ N Mid |
| line-2 | 23.6 km | 7 | 50 | SE Outer ↔ W Mid |
| line-3 | 12.7 km | 6 | 28 | NW Mid ↔ NE Mid |
| **Total** | **53.5 km** | **21 unique** | **115** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 24,859 train-km/day |
| Annual traction demand | 117.6 GWh |
| Station/depot PV / storage | 10.4 MW / 49.0 MWh |
| Aggregate charging power | 9.5 MW |
| Dedicated solar plant | 65.2 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 12.1 km / 90 kWh |
| Lowest traversal charging margin | line-3: 42 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $150 M |
| Stations | $88 M |
| Depots | $8.0 M |
| Rolling stock | $104 M |
| Dedicated solar plant | $52 M |
| Residual train control | $2.7 M |
| Charging microgrids | $2.0 M |
| EPC / project services | $25 M |
| **Total city programme** | **$431 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $108 M (25.0%) |
| Domestic / local capital | $323 M (75.0%) |
| Annual public construction commitment | $44 M / yr for 7 years |
| Annual post-grace debt service | $37 M / yr |
| External capital saved vs default turnkey sensitivity | $668 M |
| Capital + lifetime external interest saved | $1.51 bn |
| Annual OPEX | $11 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 239 assets / 1,124 tasks | [`kisumu-operations-manifest.json`](operations/kisumu-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`kisumu.toml`](kisumu.toml) | Expanded simulator scenario |
| [`kisumu.corridor.geojson`](kisumu.corridor.geojson) | GIS corridor and stations |
| [`kisumu.design-quality.yaml`](kisumu.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh kisumu
```
