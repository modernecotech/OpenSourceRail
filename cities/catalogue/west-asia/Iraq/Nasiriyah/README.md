# Nasiriyah — Urban Rail Network

**Country:** IQ · **Population:** 705,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Nasiriyah-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$844 M (87.0%) of external capital** and **$1.04 bn of external interest**. Capital plus saved interest totals **$1.88 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Nasiriyah rail network on OpenStreetMap](nasiriyah-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 20 / 3 |
| Route length | 51.1 km double track |
| Coverage / transfer reachability | 58.9% / 67% |
| Estimated station catchment | 415,245 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 147 × 3-car `light-metro-3car` trainsets (132 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 29.2 km | 9 | 82 | SE Outer ↔ NW Outer |
| line-2 | 14.0 km | 7 | 41 | N Mid ↔ W Mid |
| line-3 |  7.9 km | 4 | 24 | SE Inner ↔ W Mid |
| **Total** | **51.1 km** | **20 unique** | **147** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 23,770 train-km/day |
| Annual traction demand | 112.4 GWh |
| Station/depot PV / storage | 10.1 MW / 48.5 MWh |
| Aggregate charging power | 9.0 MW |
| Dedicated solar plant | 47.4 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 13.2 km / 106 kWh |
| Lowest traversal charging margin | line-3: 28 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $226 M |
| Stations | $97 M |
| Depots | $8.0 M |
| Rolling stock | $132 M |
| Dedicated solar plant | $38 M |
| Residual train control | $2.6 M |
| Charging microgrids | $2.0 M |
| EPC / project services | $33 M |
| **Total city programme** | **$539 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $126 M (23.3%) |
| Domestic / local capital | $413 M (76.7%) |
| Annual public construction commitment | $50 M / yr for 5 years |
| Annual post-grace debt service | $37 M / yr |
| External capital saved vs default turnkey sensitivity | $844 M |
| Capital + lifetime external interest saved | $1.88 bn |
| Annual OPEX | $15 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 273 assets / 1,340 tasks | [`nasiriyah-operations-manifest.json`](operations/nasiriyah-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`nasiriyah.toml`](nasiriyah.toml) | Expanded simulator scenario |
| [`nasiriyah.corridor.geojson`](nasiriyah.corridor.geojson) | GIS corridor and stations |
| [`nasiriyah.design-quality.yaml`](nasiriyah.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh nasiriyah
```
