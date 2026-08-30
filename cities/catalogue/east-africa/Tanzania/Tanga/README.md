# Tanga — Urban Rail Network

**Country:** TZ · **Population:** 400,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Tanga-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$654 M (86.3%) of external capital** and **$820 M of external interest**. Capital plus saved interest totals **$1.47 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Tanga rail network on OpenStreetMap](tanga-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 20 / 2 |
| Route length | 50.1 km double track |
| Coverage / transfer reachability | 52.2% / 67% |
| Estimated station catchment | 208,800 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 108 × 3-car `light-metro-3car` trainsets (97 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 21.4 km | 7 | 46 | NW Mid ↔ SE Outer |
| line-2 | 15.2 km | 7 | 32 | W Mid ↔ NE Mid |
| line-3 | 13.5 km | 6 | 30 | NE Mid ↔ W Mid |
| **Total** | **50.1 km** | **20 unique** | **108** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 23,287 train-km/day |
| Annual traction demand | 110.2 GWh |
| Station/depot PV / storage | 10.7 MW / 49.5 MWh |
| Aggregate charging power | 10.0 MW |
| Dedicated solar plant | 60.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 5.1 km / 38 kWh |
| Lowest traversal charging margin | line-2: 46 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $144 M |
| Stations | $94 M |
| Depots | $8.0 M |
| Rolling stock | $97 M |
| Dedicated solar plant | $48 M |
| Residual train control | $2.5 M |
| Charging microgrids | $2.2 M |
| EPC / project services | $24 M |
| **Total city programme** | **$421 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $104 M (24.7%) |
| Domestic / local capital | $317 M (75.3%) |
| Annual public construction commitment | $38 M / yr for 7 years |
| Annual post-grace debt service | $31 M / yr |
| External capital saved vs default turnkey sensitivity | $654 M |
| Capital + lifetime external interest saved | $1.47 bn |
| Annual OPEX | $11 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 229 assets / 1,066 tasks | [`tanga-operations-manifest.json`](operations/tanga-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`tanga.toml`](tanga.toml) | Expanded simulator scenario |
| [`tanga.corridor.geojson`](tanga.corridor.geojson) | GIS corridor and stations |
| [`tanga.design-quality.yaml`](tanga.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh tanga
```
