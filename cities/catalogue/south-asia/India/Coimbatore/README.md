# Coimbatore — Urban Rail Network

**Country:** IN · **Population:** 3,084,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Coimbatore-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$5.76 bn (85.3%) of external capital** and **$7.08 bn of external interest**. Capital plus saved interest totals **$12.83 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Coimbatore rail network on OpenStreetMap](coimbatore-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 9 / 111 / 19 |
| Route length | 342.0 km double track |
| Coverage / transfer reachability | 73.5% / 47% |
| Estimated station catchment | 2,266,740 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 540 × 6-car `metro-6car` trainsets (487 peak revenue) |
| Peak network throughput | 259,200 passengers/hour |
| Practical service capacity | 2,276,640 passenger-trips/day |
| Annual paid-trip planning range | 415.5–664.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 48.2 km | 17 | 95 | SW Outer ↔ NE Outer |
| line-2 | 28.4 km | 10 | 51 | E Mid ↔ W Mid |
| line-3 | 32.8 km | 12 | 64 | N Outer ↔ SW Mid |
| line-4 | 32.2 km | 8 | 60 | S Mid ↔ NE Outer |
| line-5 | 31.1 km | 10 | 58 | NW Mid ↔ E Outer |
| line-6 | 37.8 km | 14 | 73 | S Outer ↔ NW Mid |
| line-7 | 23.4 km | 9 | 43 | W Outer ↔ SE Inner |
| line-8 | 32.1 km | 10 | 60 | S Mid ↔ N Mid |
| line-9 | 76.1 km | 21 | 36 | W Mid ↔ W Mid |
| **Total** | **342.0 km** | **111 unique** | **540** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 3,952 one-way journeys / 141,321 train-km/day |
| Annual traction demand | 1,337.0 GWh |
| Station/depot PV / storage | 33.5 MW / 230.0 MWh |
| Aggregate charging power | 192.0 MW |
| Dedicated solar plant | 839.1 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-9: 19.0 km / 285 kWh |
| Lowest traversal charging margin | line-7: 202 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.27 bn |
| Stations | $631 M |
| Depots | $8.0 M |
| Rolling stock | $907 M |
| Dedicated solar plant | $671 M |
| Residual train control | $17 M |
| Charging microgrids | $42 M |
| EPC / project services | $201 M |
| **Total city programme** | **$3.75 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $994 M (26.5%) |
| Domestic / local capital | $2.76 bn (73.5%) |
| Annual public construction commitment | $314 M / yr for 5 years |
| Annual post-grace debt service | $231 M / yr |
| External capital saved vs default turnkey sensitivity | $5.76 bn |
| Capital + lifetime external interest saved | $12.83 bn |
| Annual OPEX | $92 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 1,179 assets / 5,470 tasks | [`coimbatore-operations-manifest.json`](operations/coimbatore-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`coimbatore.toml`](coimbatore.toml) | Expanded simulator scenario |
| [`coimbatore.corridor.geojson`](coimbatore.corridor.geojson) | GIS corridor and stations |
| [`coimbatore.design-quality.yaml`](coimbatore.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh coimbatore
```
