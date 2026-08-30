# Dodoma — Urban Rail Network

**Country:** TZ · **Population:** 800,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Dodoma-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$641 M (86.6%) of external capital** and **$803 M of external interest**. Capital plus saved interest totals **$1.44 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Dodoma rail network on OpenStreetMap](dodoma-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 22 / 1 |
| Route length | 52.2 km double track |
| Coverage / transfer reachability | 58.1% / 100% |
| Estimated station catchment | 464,799 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 113 × 3-car `light-metro-3car` trainsets (101 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 16.5 km | 8 | 36 | S Mid ↔ N Mid |
| line-2 | 17.6 km | 7 | 37 | SW Mid ↔ E Outer |
| line-3 | 18.1 km | 7 | 40 | NW Outer ↔ SE Inner |
| **Total** | **52.2 km** | **22 unique** | **113** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 24,262 train-km/day |
| Annual traction demand | 114.8 GWh |
| Station/depot PV / storage | 11.0 MW / 50.0 MWh |
| Aggregate charging power | 10.5 MW |
| Dedicated solar plant | 43.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 7.0 km / 59 kWh |
| Lowest traversal charging margin | line-2: 39 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $147 M |
| Stations | $90 M |
| Depots | $8.0 M |
| Rolling stock | $102 M |
| Dedicated solar plant | $34 M |
| Residual train control | $2.6 M |
| Charging microgrids | $2.2 M |
| EPC / project services | $25 M |
| **Total city programme** | **$411 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $99 M (24.1%) |
| Domestic / local capital | $312 M (75.9%) |
| Annual public construction commitment | $37 M / yr for 7 years |
| Annual post-grace debt service | $31 M / yr |
| External capital saved vs default turnkey sensitivity | $641 M |
| Capital + lifetime external interest saved | $1.44 bn |
| Annual OPEX | $11 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 242 assets / 1,127 tasks | [`dodoma-operations-manifest.json`](operations/dodoma-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`dodoma.toml`](dodoma.toml) | Expanded simulator scenario |
| [`dodoma.corridor.geojson`](dodoma.corridor.geojson) | GIS corridor and stations |
| [`dodoma.design-quality.yaml`](dodoma.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh dodoma
```
