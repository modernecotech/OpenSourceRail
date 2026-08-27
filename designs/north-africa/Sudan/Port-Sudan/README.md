# Port-Sudan — Urban Rail Network

**Country:** SD · **Population:** 500,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Port-Sudan-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$503 M (87.0%) of external capital** and **$649 M of external interest**. Capital plus saved interest totals **$1.15 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Port-Sudan rail network on OpenStreetMap](port-sudan-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 15 / 2 |
| Route length | 33.9 km double track |
| Coverage / transfer reachability | 80.3% / 100% |
| Estimated station catchment | 401,500 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 76 × 3-car `light-metro-3car` trainsets (68 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 13.5 km | 6 | 30 | N Outer ↔ S Outer |
| line-2 | 11.3 km | 5 | 26 | NW Outer ↔ S Mid |
| line-3 |  9.1 km | 4 | 20 | NE Mid ↔ S Mid |
| **Total** | **33.9 km** | **15 unique** | **76** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 15,757 train-km/day |
| Annual traction demand | 74.5 GWh |
| Station/depot PV / storage | 9.2 MW / 47.0 MWh |
| Aggregate charging power | 7.5 MW |
| Dedicated solar plant | 28.6 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 3.4 km / 28 kWh |
| Lowest traversal charging margin | line-3: 34 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $109 M |
| Stations | $90 M |
| Depots | $8.0 M |
| Rolling stock | $68 M |
| Dedicated solar plant | $23 M |
| Residual train control | $1.7 M |
| Charging microgrids | $1.8 M |
| EPC / project services | $19 M |
| **Total city programme** | **$321 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $75 M (23.4%) |
| Domestic / local capital | $246 M (76.6%) |
| Annual public construction commitment | $38 M / yr for 10 years |
| Annual post-grace debt service | $35 M / yr |
| External capital saved vs default turnkey sensitivity | $503 M |
| Capital + lifetime external interest saved | $1.15 bn |
| Annual OPEX | $7.8 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 168 assets / 763 tasks | [`port-sudan-operations-manifest.json`](operations/port-sudan-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`port-sudan.toml`](port-sudan.toml) | Expanded simulator scenario |
| [`port-sudan.corridor.geojson`](port-sudan.corridor.geojson) | GIS corridor and stations |
| [`port-sudan.design-quality.yaml`](port-sudan.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
scripts/regenerate-city.sh port-sudan
```
