# Damanhur — Urban Rail Network

**Country:** EG · **Population:** 500,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Damanhur-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$596 M (86.5%) of external capital** and **$733 M of external interest**. Capital plus saved interest totals **$1.33 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Damanhur rail network on OpenStreetMap](damanhur-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 18 / 1 |
| Route length | 47.4 km double track |
| Coverage / transfer reachability | 85.7% / 100% |
| Estimated station catchment | 428,500 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 103 × 3-car `light-metro-3car` trainsets (92 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 |  9.4 km | 5 | 23 | NW Mid ↔ S Mid |
| line-2 | 18.3 km | 7 | 40 | E Outer ↔ W Mid |
| line-3 | 19.8 km | 6 | 40 | SW Outer ↔ NE Outer |
| **Total** | **47.4 km** | **18 unique** | **103** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 22,049 train-km/day |
| Annual traction demand | 104.3 GWh |
| Station/depot PV / storage | 9.8 MW / 48.0 MWh |
| Aggregate charging power | 8.5 MW |
| Dedicated solar plant | 43.5 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 7.0 km / 56 kWh |
| Lowest traversal charging margin | line-1: 39 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $136 M |
| Stations | $84 M |
| Depots | $8.0 M |
| Rolling stock | $93 M |
| Dedicated solar plant | $35 M |
| Residual train control | $2.4 M |
| Charging microgrids | $1.9 M |
| EPC / project services | $23 M |
| **Total city programme** | **$383 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $93 M (24.2%) |
| Domestic / local capital | $290 M (75.8%) |
| Annual public construction commitment | $40 M / yr for 5 years |
| Annual post-grace debt service | $30 M / yr |
| External capital saved vs default turnkey sensitivity | $596 M |
| Capital + lifetime external interest saved | $1.33 bn |
| Annual OPEX | $10 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 212 assets / 997 tasks | [`damanhur-operations-manifest.json`](operations/damanhur-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`damanhur.toml`](damanhur.toml) | Expanded simulator scenario |
| [`damanhur.corridor.geojson`](damanhur.corridor.geojson) | GIS corridor and stations |
| [`damanhur.design-quality.yaml`](damanhur.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
scripts/regenerate-city.sh damanhur
```
