# Tanta — Urban Rail Network

**Country:** EG · **Population:** 750,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Tanta-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$849 M (85.9%) of external capital** and **$1.04 bn of external interest**. Capital plus saved interest totals **$1.89 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Tanta rail network on OpenStreetMap](tanta-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 25 / 1 |
| Route length | 74.9 km double track |
| Coverage / transfer reachability | 56.5% / 100% |
| Estimated station catchment | 423,749 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 176 × 3-car `light-metro-3car` trainsets (158 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 18.2 km | 8 | 45 | N Mid ↔ SW Outer |
| line-2 | 27.8 km | 8 | 64 | NW Outer ↔ SE Outer |
| line-3 | 28.9 km | 9 | 67 | SW Outer ↔ NE Outer |
| **Total** | **74.9 km** | **25 unique** | **176** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 34,838 train-km/day |
| Annual traction demand | 164.8 GWh |
| Station/depot PV / storage | 10.7 MW / 59.0 MWh |
| Aggregate charging power | 20.0 MW |
| Dedicated solar plant | 74.2 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 11.9 km / 96 kWh |
| Lowest traversal charging margin | line-3: 94 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $195 M |
| Stations | $88 M |
| Depots | $8.0 M |
| Rolling stock | $158 M |
| Dedicated solar plant | $59 M |
| Residual train control | $3.7 M |
| Charging microgrids | $4.3 M |
| EPC / project services | $32 M |
| **Total city programme** | **$549 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $139 M (25.4%) |
| Domestic / local capital | $410 M (74.6%) |
| Annual public construction commitment | $57 M / yr for 5 years |
| Annual post-grace debt service | $43 M / yr |
| External capital saved vs default turnkey sensitivity | $849 M |
| Capital + lifetime external interest saved | $1.89 bn |
| Annual OPEX | $15 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 326 assets / 1,611 tasks | [`tanta-operations-manifest.json`](operations/tanta-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`tanta.toml`](tanta.toml) | Expanded simulator scenario |
| [`tanta.corridor.geojson`](tanta.corridor.geojson) | GIS corridor and stations |
| [`tanta.design-quality.yaml`](tanta.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh tanta
```
